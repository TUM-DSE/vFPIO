#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <assert.h>
#include <err.h>
#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <malloc.h>
#include <mm_malloc.h>
#include <zlib.h>

const char* SOCKET_NAME = "/tmp/serverless.sock";
const int MSG_SIZE = 4096;
int sockfd = -1;

void serverless_connect() {
    struct sockaddr_un addr;
    int sfd = socket(AF_UNIX, SOCK_STREAM, 0);
    printf("Client socket fd = %d\n", sfd);
    
    if(sfd==-1) {
        perror("socket() error");
        return;
    }


    memset(&addr, 0, sizeof(struct sockaddr_un));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_NAME, sizeof(addr.sun_path)-1);

    if(connect(sfd, (struct sockaddr*) &addr, sizeof(addr))==-1) {
        perror("connect() error");
        return;
    }

    sockfd = sfd;
}

void serverless_write_sock(const char* const str) {
    if(strlen(str) >= MSG_SIZE) {
        printf("message too long\n");
        return;
    }

    char msg[MSG_SIZE];
    memset(msg, 0, sizeof(msg));
    strncpy(msg, str, MSG_SIZE);

    printf("writing: %s\n", msg);

    if(write(sockfd, msg, MSG_SIZE) == -1) {
        perror("write() error");
        return;
    }

    //wait for response
    memset(msg, 0, sizeof(msg));
    int bytes = read(sockfd, msg, MSG_SIZE);
    if(bytes <= 0) {
        perror("read() error");
    }
    printf("got response: %s\n", msg);
}

void serverless_set_csr(uint32_t offset, uint64_t value)
{
    if(sockfd<0) {
        printf("serverless_set_csr() not connected");
        return;
    }

    char str[4096];
    snprintf(str, sizeof(str), "SET_CSR %u %lu", offset, value);
    serverless_write_sock(str);
}

void serverless_load_bitstream(uint32_t config)
{
    if(sockfd<0) {
        printf("serverless_load_bitstream() not connected");
        return;
    }

    char str[4096];
    snprintf(str, sizeof(str), "BITSTREAM %u", config);
    serverless_write_sock(str);
}

void serverless_map_memory(void *addr, size_t len, size_t input_len, size_t output_len)
{
    if(sockfd<0) {
        printf("serverless_map_memory() not connected");
        return;
    }

    char str[4096];
    snprintf(str, sizeof(str), "USERMAP %lu %lu %lu %lu", (uint64_t)addr, len, input_len, output_len);
    serverless_write_sock(str);
}

void serverless_exec() {
    if(sockfd<0) {
        printf("exec() not connected");
        return;
    }

    serverless_write_sock("LAUNCH");
}

void serverless_exit() {
    if(sockfd<0) {
        printf("exit() not connected");
        return;
    }

    serverless_write_sock("TEARDOWN");
}


//#define SIZE 64
#define SIZE 65536
//#define SIZE 3000001
#define ALIGNMENT 64
char memUnaligned[SIZE+ALIGNMENT];
int hls4ml_samples = 0;


void prepare_sha3(void *mem, int bytes)
{
    for(int i=0; i<bytes; i++) {
        ((char*)mem)[i] = 'a';
    }
    ((char*)mem)[0] = 'b';
    ((char*)mem)[66] = 'c';

    serverless_map_memory(mem, bytes, 128, 64);
    serverless_load_bitstream(0);
}

void check_sha3(void *mem, int bytes)
{
    printf("Check SHA3: ");
    for(int i=0; i<8; i++) {
        printf("%lx", ((uint64_t*)mem)[7-i]);
    }
    printf("\n");
}

void prepare_aes(void *mem, int bytes)
{

    uint64_t const keyLow = 0xabf7158809cf4f3c;
    uint64_t const keyHigh = 0x2b7e151628aed2a6;
    uint64_t const plainLow = 0xe93d7e117393172a;
    uint64_t const plainHigh = 0x6bc1bee22e409f96;

    serverless_map_memory(mem, bytes, bytes, bytes);
    serverless_load_bitstream(1);
    serverless_set_csr(0, keyLow);
    serverless_set_csr(1, keyHigh);

    for(int i=0; i<(int)(bytes/sizeof(uint64_t)); i++) {
        ((uint64_t*)mem)[i]= i%2?plainHigh:plainLow;
    }
}

void check_aes(void *mem, int bytes)
{
    uint64_t const cipherLow = 0xa89ecaf32466ef97;
    uint64_t const cipherHigh = 0x3ad77bb40d7a3660;
    bool correct=true;

    for(int i=0; i<(int)(bytes/sizeof(uint64_t)); i++) {
        correct &= ((uint64_t*)mem)[i] == (i%2?cipherHigh:cipherLow);
    }

    printf("Check AES: result is %s\n", correct ? "correct :)" : "wrong !!");
}


void prepare_addmul(void *mem, int bytes) {
    const int add=5;
    const int mul=2;

    for(int i=0; i<(int)(bytes/sizeof(uint32_t)); i++) {
        ((uint32_t*)mem)[i]=i;
    }

    serverless_map_memory(mem, bytes, bytes, bytes);
    serverless_load_bitstream(2);
    serverless_set_csr(0, mul);
    serverless_set_csr(1, add);
}

void check_addmul(void *mem, int bytes)
{
    const int add=5;
    const int mul=2;
    bool correct=true;

    for(int i=0; i<(int)(bytes/sizeof(uint32_t)); i++) {
        correct &= ((uint32_t*)mem)[i] == (((uint32_t)i)<<mul)+add;
    }

    printf("Check AddMul: result is %s\n", correct ? "correct :)" : "wrong !!");
}


void prepare_sha256hls(void *mem, int bytes)
{
    for(int i=0; i<bytes; i++) {
        ((char*)mem)[i] = 'f';
    }
    //((char*)mem)[0] = 'b';
    //((char*)mem)[66] = 'c';

    serverless_map_memory(mem, bytes, 64, 32);
    serverless_load_bitstream(3);
}

void check_sha256hls(void *mem, int bytes)
{
    printf("Check SHA-256: ");
    for(int i=0; i<32; i++) {
        printf("%02x", ((uint8_t*)mem)[i]);
    }
    printf("\n");
    for(int i=0; i<32; i++) {
        uint8_t b = ((uint8_t*)mem)[i];
        b = (b * 0x0202020202ULL & 0x010884422010ULL) % 1023;
        printf("%02x", b);
    }
    printf("\n");
}

void prepare_nw(void *mem, int bytes)
{
    const uint64_t s_ratio = 512/128;
    const uint64_t sc_ratio = 512/8;
    const uint64_t s0_words = 32;
    const uint64_t s1_words = 32;
    const uint64_t sc_count = s0_words*s_ratio * s1_words*s_ratio;
    const uint64_t sc_words = (sc_count+sc_ratio-1)/sc_ratio;
    
    assert((s0_words+s1_words+1)*64 < bytes);
    assert(sc_words*64 < bytes);
    
    ((uint64_t*)mem)[0] = s0_words;
    ((uint64_t*)mem)[1] = s1_words;
    ((uint64_t*)mem)[2] = sc_count;
    ((uint64_t*)mem)[3] = sc_words;
    
    for(uint32_t i=0; i<s0_words+s1_words; i++)
        for(uint32_t j=0; j<64; j++)
            ((uint8_t*)mem)[(i+1)*64+j] = (i*31+j*37)%251;

    serverless_map_memory(mem, bytes, (s0_words+s1_words+1)*64, sc_words*64);
    serverless_load_bitstream(4);
}

void check_nw(void *mem, int bytes)
{
    printf("Check NW: \n");
    for(int j=0; j<2; j++) {
    for(int i=0; i<64; i++) {
        printf("%02x ", ((uint8_t*)mem)[j*64+i]);
        }
        printf("\n");
    }
    printf("\n");
}


void prepare_hls4ml(void *mem, int bytes)
{
    FILE * fd;
    fd = fopen("tb_input_features.dat","r");
    if(fd==NULL) {
        perror("could not open file");
        exit(1);
    }

    short *smem = (short*)mem;
    float fpv;

    for(int i=0; fscanf(fd, "%f", &fpv)>0; i++) {
        assert(i*2 <= bytes);

        short fixp = fpv*(1<<10) + 0.5;
        smem[i] = fixp;
        hls4ml_samples = (i+1)/32/32/3;
    }
    fclose(fd);

    serverless_map_memory(mem, bytes, hls4ml_samples*32*32*3*2, hls4ml_samples*64);
    serverless_load_bitstream(5);
}

void check_hls4ml(void *mem, int bytes)
{
    printf("Check hls4ml: ");
    short *smem = (short*)mem;
    for(int i=0; i<hls4ml_samples; i++) {
        int maxarg=-1;
        float maxval=-1;
        for(int j=0; j<10; j++) {
            short fixp = smem[i*32+j];
            float fpv = ((float)fixp)/(1<<10);
            printf("%.4f ", fpv);
            if(fpv > maxval) {
                maxarg = j;
                maxval = fpv;
            }
        }
        printf(" -->  %d \n", maxarg);
    }
}

void prepare_matmul(void *mem, int bytes)
{
    const int MAT_BYTES = 64*64*8;
    assert(bytes >= 2*MAT_BYTES);
    
    for(int i=0; i<bytes/8; i++) {
	((uint64_t*)mem)[i] = -2345+i;
    }

    serverless_map_memory(mem, bytes, 2*MAT_BYTES, MAT_BYTES);
    serverless_load_bitstream(6);
}

void check_matmul(void *mem, int bytes)
{
    printf("Check MatMul: \n");
    for(int r=0; r<64*64/8; r++) {
        for(int i=0; i<8; i++) {
        printf("%ld ", ((uint64_t*)mem)[r*8+i]);
        }
        printf("\n");
    }
    printf("\n");
}

void prepare_gzip(void *mem, int bytes)
{
    for(int i=0; i<bytes; i++) {
        char c = '0'+(i%('z'-'0'));
        ((char*)mem)[i] = c;
    }

    serverless_map_memory(mem, 2048, 512, 128);
    serverless_load_bitstream(7);
}

void check_gzip(void *mem, int bytes)
{
    printf("Check Gzip: \n");
    for(int j=0; j<2; j++) {
    for(int i=0; i<64; i++) {
        printf("%02x ", ((unsigned char*)mem)[j*64+i]);
        }
        printf("\n");
    }
    printf("\n");
}

void prepare_sha256(void *mem, int bytes)
{

    uint64_t const keyLow = 0xabf7158809cf4f3c;
    uint64_t const keyHigh = 0x2b7e151628aed2a6;
    uint64_t const plainLow = 0xe93d7e117393172a;
    uint64_t const plainHigh = 0x6bc1bee22e409f96;

    serverless_map_memory(mem, bytes, bytes, bytes);
    serverless_load_bitstream(0);
    // serverless_set_csr(0, keyLow);
    // serverless_set_csr(1, keyHigh);

    for(int i=0; i<(int)(bytes/sizeof(uint64_t)); i++) {
        ((uint64_t*)mem)[i]= i%2?plainHigh:plainLow;
    }
}

void check_sha256(void *mem, int bytes)
{
    uint64_t const cipherLow = 0xa89ecaf32466ef97;
    uint64_t const cipherHigh = 0x3ad77bb40d7a3660;
    bool correct=true;

    // for(int i=0; i<(int)(bytes/sizeof(uint64_t)); i++) {
    //     correct &= ((uint64_t*)mem)[i] == (i%2?cipherHigh:cipherLow);
    // }

    // printf("Check sha256: result is %s\n", correct ? "correct :)" : "wrong !!");
}

void prepare_md5(void *mem, int bytes)
{

    uint64_t const keyLow = 0xabf7158809cf4f3c;
    uint64_t const keyHigh = 0x2b7e151628aed2a6;
    uint64_t const plainLow = 0xe93d7e117393172a;
    uint64_t const plainHigh = 0x6bc1bee22e409f96;

    serverless_map_memory(mem, bytes, bytes, bytes);
    serverless_load_bitstream(1);
    // serverless_set_csr(0, keyLow);
    // serverless_set_csr(1, keyHigh);

    for(int i=0; i<(int)(bytes/sizeof(uint64_t)); i++) {
        ((uint64_t*)mem)[i]= i%2?plainHigh:plainLow;
    }
}

void check_md5(void *mem, int bytes)
{
    uint64_t const cipherLow = 0xa89ecaf32466ef97;
    uint64_t const cipherHigh = 0x3ad77bb40d7a3660;
    bool correct=true;

    // for(int i=0; i<(int)(bytes/sizeof(uint64_t)); i++) {
    //     correct &= ((uint64_t*)mem)[i] == (i%2?cipherHigh:cipherLow);
    // }

    // printf("Check sha256: result is %s\n", correct ? "correct :)" : "wrong !!");
}


int main(int argc, char* argv[])
{
    int op=-1;

    if(argc<2) op=-1;
    else if(!strcmp(argv[1], "aes")) op = 0;
    else if(!strcmp(argv[1], "addmul")) op = 1;
    else if(!strcmp(argv[1], "sha3")) op = 2;
    else if(!strcmp(argv[1], "matmul")) op = 3;
    else if(!strcmp(argv[1], "gzip")) op = 4;
    else if(!strcmp(argv[1], "nw")) op = 5;
    else if(!strcmp(argv[1], "sha256hls")) op = 6;
    else if(!strcmp(argv[1], "hls4ml")) op = 7;
    else if(!strcmp(argv[1], "sha256")) op = 8;
    else if(!strcmp(argv[1], "md5")) op = 9;
    
    printf("op = %d\n", op);
    if(op<0) {
        return 1;
    }

    // puts("\n**** serverless_example.c ****\n\n");
    // printf("op = %d\n", op);
    serverless_connect();

    void *mem = memUnaligned + ALIGNMENT - ((int64_t)memUnaligned)%ALIGNMENT;

    for (int i = 0; i < 10; i++) {
        printf("i = %d\n", i);
        puts("-------------------------------");
        // op = 8;
        puts("guest: start...\n");
        if(op==0) prepare_aes(mem, SIZE);
        if(op==1) prepare_addmul(mem, SIZE);
        if(op==2) prepare_sha3(mem, SIZE);
        if(op==3) prepare_matmul(mem, SIZE);
        if(op==4) prepare_gzip(mem, SIZE);
        if(op==5) prepare_nw(mem, SIZE);
        if(op==6) prepare_sha256hls(mem, SIZE);
        if(op==7) prepare_hls4ml(mem, SIZE);
        if(op==8) prepare_sha256(mem, SIZE);
        if(op==9) prepare_md5(mem, SIZE);
        
        prepare_sha256(mem, SIZE);
        //prepare_sha3(mem, SIZE);
        // serverless_exec();
        // if(op==0) check_aes(mem, SIZE);
        // if(op==1) check_addmul(mem, SIZE);
        // if(op==2) check_sha3(mem, SIZE);
        // if(op==3) check_matmul(mem, SIZE);
        // if(op==4) check_gzip(mem, SIZE);
        // if(op==5) check_nw(mem, SIZE);
        // if(op==6) check_sha256hls(mem, SIZE);
        // if(op==7) check_hls4ml(mem, SIZE);
        // if(op==8) check_sha256(mem, SIZE);
        // if(op==9) check_md5(mem, SIZE);
        // //check_sha3(mem, SIZE);
        puts("guest: finish...\n");        
        sleep(1);
    }

    puts("results: ");
    for(int i=0; i<16; i++) {
        uint64_t val = ((uint64_t*)mem)[i];
        printf("%s 0x%lx", (i==0 ? "" : ","), val);
    }
    puts(" ...\n");

    // serverless_exit();

    return 0;
}
