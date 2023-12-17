-- ==============================================================
-- RTL generated by Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.1 (64-bit)
-- Version: 2022.1
-- Copyright (C) Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- 
-- ===========================================================

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity sha256_axis_fpga_sha256_digester is
port (
    ap_clk : IN STD_LOGIC;
    ap_rst : IN STD_LOGIC;
    k : IN STD_LOGIC_VECTOR (31 downto 0);
    rx_state : IN STD_LOGIC_VECTOR (255 downto 0);
    rx_w : IN STD_LOGIC_VECTOR (511 downto 0);
    ap_return : OUT STD_LOGIC_VECTOR (767 downto 0);
    ap_ce : IN STD_LOGIC );
end;


architecture behav of sha256_axis_fpga_sha256_digester is 
    constant ap_const_logic_1 : STD_LOGIC := '1';
    constant ap_const_boolean_1 : BOOLEAN := true;
    constant ap_const_boolean_0 : BOOLEAN := false;
    constant ap_const_lv32_2 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000000000010";
    constant ap_const_lv32_1F : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000000011111";
    constant ap_const_lv32_D : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000000001101";
    constant ap_const_lv32_16 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000000010110";
    constant ap_const_lv32_80 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000010000000";
    constant ap_const_lv32_9F : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000010011111";
    constant ap_const_lv32_86 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000010000110";
    constant ap_const_lv32_85 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000010000101";
    constant ap_const_lv32_8B : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000010001011";
    constant ap_const_lv32_8A : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000010001010";
    constant ap_const_lv32_99 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000010011001";
    constant ap_const_lv32_98 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000010011000";
    constant ap_const_lv32_A0 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000010100000";
    constant ap_const_lv32_BF : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000010111111";
    constant ap_const_lv32_C0 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000011000000";
    constant ap_const_lv32_DF : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000011011111";
    constant ap_const_lv32_20 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000000100000";
    constant ap_const_lv32_3F : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000000111111";
    constant ap_const_lv32_40 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000001000000";
    constant ap_const_lv32_5F : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000001011111";
    constant ap_const_lv32_24 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000000100100";
    constant ap_const_lv32_26 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000000100110";
    constant ap_const_lv32_2F : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000000101111";
    constant ap_const_lv32_31 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000000110001";
    constant ap_const_lv32_27 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000000100111";
    constant ap_const_lv32_23 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000000100011";
    constant ap_const_lv32_32 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000000110010";
    constant ap_const_lv32_2E : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000000101110";
    constant ap_const_lv32_1C7 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000111000111";
    constant ap_const_lv32_1D0 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000111010000";
    constant ap_const_lv32_1C9 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000111001001";
    constant ap_const_lv32_1D2 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000111010010";
    constant ap_const_lv32_1D1 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000111010001";
    constant ap_const_lv32_1DF : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000111011111";
    constant ap_const_lv32_1C0 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000111000000";
    constant ap_const_lv32_1C6 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000111000110";
    constant ap_const_lv32_1D3 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000111010011";
    constant ap_const_lv32_1C8 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000111001000";
    constant ap_const_lv32_1CA : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000111001010";
    constant ap_const_lv32_E0 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000011100000";
    constant ap_const_lv32_FF : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000011111111";
    constant ap_const_lv32_120 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000100100000";
    constant ap_const_lv32_13F : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000100111111";
    constant ap_const_lv32_1FF : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000111111111";
    constant ap_const_lv32_60 : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000001100000";
    constant ap_const_lv32_7F : STD_LOGIC_VECTOR (31 downto 0) := "00000000000000000000000001111111";
    constant ap_const_logic_0 : STD_LOGIC := '0';

attribute shreg_extract : string;
    signal ret_V_fu_272_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal ret_V_reg_815 : STD_LOGIC_VECTOR (31 downto 0);
    signal ap_block_state1_pp0_stage0_iter0 : BOOLEAN;
    signal ap_block_state2_pp0_stage0_iter1 : BOOLEAN;
    signal ap_block_pp0_stage0_11001 : BOOLEAN;
    signal ret_V_10_fu_460_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal ret_V_10_reg_820 : STD_LOGIC_VECTOR (31 downto 0);
    signal t1_V_fu_722_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal t1_V_reg_825 : STD_LOGIC_VECTOR (31 downto 0);
    signal new_w_V_fu_750_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal new_w_V_reg_831 : STD_LOGIC_VECTOR (31 downto 0);
    signal tmp_22_reg_836 : STD_LOGIC_VECTOR (479 downto 0);
    signal tmp_23_reg_841 : STD_LOGIC_VECTOR (31 downto 0);
    signal tmp_24_reg_846 : STD_LOGIC_VECTOR (95 downto 0);
    signal trunc_ln312_fu_786_p1 : STD_LOGIC_VECTOR (95 downto 0);
    signal trunc_ln312_reg_851 : STD_LOGIC_VECTOR (95 downto 0);
    signal ap_block_pp0_stage0 : BOOLEAN;
    signal trunc_ln674_fu_210_p1 : STD_LOGIC_VECTOR (1 downto 0);
    signal tmp_fu_200_p4 : STD_LOGIC_VECTOR (29 downto 0);
    signal trunc_ln674_1_fu_232_p1 : STD_LOGIC_VECTOR (12 downto 0);
    signal tmp_5_fu_222_p4 : STD_LOGIC_VECTOR (18 downto 0);
    signal trunc_ln674_2_fu_254_p1 : STD_LOGIC_VECTOR (21 downto 0);
    signal tmp_7_fu_244_p4 : STD_LOGIC_VECTOR (9 downto 0);
    signal temp0_V_fu_214_p3 : STD_LOGIC_VECTOR (31 downto 0);
    signal temp2_V_fu_258_p3 : STD_LOGIC_VECTOR (31 downto 0);
    signal xor_ln1545_fu_266_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal temp1_V_fu_236_p3 : STD_LOGIC_VECTOR (31 downto 0);
    signal tmp_1_fu_298_p4 : STD_LOGIC_VECTOR (5 downto 0);
    signal tmp_9_fu_288_p4 : STD_LOGIC_VECTOR (25 downto 0);
    signal tmp_3_fu_326_p4 : STD_LOGIC_VECTOR (10 downto 0);
    signal tmp_2_fu_316_p4 : STD_LOGIC_VECTOR (20 downto 0);
    signal tmp_s_fu_354_p4 : STD_LOGIC_VECTOR (24 downto 0);
    signal tmp_4_fu_344_p4 : STD_LOGIC_VECTOR (6 downto 0);
    signal temp0_V_1_fu_308_p3 : STD_LOGIC_VECTOR (31 downto 0);
    signal temp2_V_1_fu_364_p3 : STD_LOGIC_VECTOR (31 downto 0);
    signal xor_ln1545_2_fu_372_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal temp1_V_1_fu_336_p3 : STD_LOGIC_VECTOR (31 downto 0);
    signal z_V_fu_394_p4 : STD_LOGIC_VECTOR (31 downto 0);
    signal y_V_fu_384_p4 : STD_LOGIC_VECTOR (31 downto 0);
    signal ret_V_4_fu_404_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal x_V_1_fu_278_p4 : STD_LOGIC_VECTOR (31 downto 0);
    signal ret_V_5_fu_410_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal y_V_1_fu_422_p4 : STD_LOGIC_VECTOR (31 downto 0);
    signal x_V_fu_196_p1 : STD_LOGIC_VECTOR (31 downto 0);
    signal z_V_1_fu_432_p4 : STD_LOGIC_VECTOR (31 downto 0);
    signal ret_V_8_fu_448_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal ret_V_9_fu_454_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal ret_V_7_fu_442_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal tmp_8_fu_476_p4 : STD_LOGIC_VECTOR (2 downto 0);
    signal tmp_6_fu_466_p4 : STD_LOGIC_VECTOR (2 downto 0);
    signal tmp_11_fu_502_p4 : STD_LOGIC_VECTOR (3 downto 0);
    signal tmp_10_fu_492_p4 : STD_LOGIC_VECTOR (24 downto 0);
    signal tmp_13_fu_530_p4 : STD_LOGIC_VECTOR (14 downto 0);
    signal tmp_12_fu_520_p4 : STD_LOGIC_VECTOR (13 downto 0);
    signal temp1_V_2_fu_512_p3 : STD_LOGIC_VECTOR (28 downto 0);
    signal temp3_V_fu_548_p4 : STD_LOGIC_VECTOR (28 downto 0);
    signal xor_ln1545_7_fu_558_p2 : STD_LOGIC_VECTOR (28 downto 0);
    signal temp2_V_2_fu_540_p3 : STD_LOGIC_VECTOR (28 downto 0);
    signal temp0_V_2_fu_486_p2 : STD_LOGIC_VECTOR (2 downto 0);
    signal ret_V_11_fu_564_p2 : STD_LOGIC_VECTOR (28 downto 0);
    signal tmp_15_fu_588_p4 : STD_LOGIC_VECTOR (9 downto 0);
    signal tmp_14_fu_578_p4 : STD_LOGIC_VECTOR (9 downto 0);
    signal tmp_17_fu_614_p4 : STD_LOGIC_VECTOR (6 downto 0);
    signal tmp_16_fu_604_p4 : STD_LOGIC_VECTOR (14 downto 0);
    signal tmp_19_fu_642_p4 : STD_LOGIC_VECTOR (8 downto 0);
    signal tmp_18_fu_632_p4 : STD_LOGIC_VECTOR (12 downto 0);
    signal temp1_V_3_fu_624_p3 : STD_LOGIC_VECTOR (21 downto 0);
    signal temp3_V_1_fu_660_p4 : STD_LOGIC_VECTOR (21 downto 0);
    signal xor_ln1545_10_fu_670_p2 : STD_LOGIC_VECTOR (21 downto 0);
    signal temp2_V_3_fu_652_p3 : STD_LOGIC_VECTOR (21 downto 0);
    signal temp0_V_3_fu_598_p2 : STD_LOGIC_VECTOR (9 downto 0);
    signal ret_V_12_fu_676_p2 : STD_LOGIC_VECTOR (21 downto 0);
    signal tmp_20_fu_690_p4 : STD_LOGIC_VECTOR (31 downto 0);
    signal trunc_ln674_3_fu_700_p1 : STD_LOGIC_VECTOR (31 downto 0);
    signal ret_V_6_fu_416_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal add_ln232_1_fu_710_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal ret_V_3_fu_378_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal add_ln232_2_fu_716_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal add_ln232_fu_704_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal p_Result_1_fu_682_p3 : STD_LOGIC_VECTOR (31 downto 0);
    signal p_Result_s_fu_570_p3 : STD_LOGIC_VECTOR (31 downto 0);
    signal tmp_21_fu_728_p4 : STD_LOGIC_VECTOR (31 downto 0);
    signal add_ln232_5_fu_744_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal add_ln232_4_fu_738_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal add_ln414_9_fu_794_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal add_ln414_fu_790_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal add_ln414_8_fu_798_p2 : STD_LOGIC_VECTOR (31 downto 0);
    signal ap_ce_reg : STD_LOGIC;


begin



    process (ap_clk)
    begin
        if (ap_clk'event and ap_clk = '1') then
            if (((ap_const_boolean_0 = ap_block_pp0_stage0_11001) and (ap_const_logic_1 = ap_ce))) then
                new_w_V_reg_831 <= new_w_V_fu_750_p2;
                ret_V_10_reg_820 <= ret_V_10_fu_460_p2;
                ret_V_reg_815 <= ret_V_fu_272_p2;
                t1_V_reg_825 <= t1_V_fu_722_p2;
                tmp_22_reg_836 <= rx_w(511 downto 32);
                tmp_23_reg_841 <= rx_state(127 downto 96);
                tmp_24_reg_846 <= rx_state(223 downto 128);
                trunc_ln312_reg_851 <= trunc_ln312_fu_786_p1;
            end if;
        end if;
    end process;
    add_ln232_1_fu_710_p2 <= std_logic_vector(unsigned(ret_V_6_fu_416_p2) + unsigned(k));
    add_ln232_2_fu_716_p2 <= std_logic_vector(unsigned(add_ln232_1_fu_710_p2) + unsigned(ret_V_3_fu_378_p2));
    add_ln232_4_fu_738_p2 <= std_logic_vector(unsigned(p_Result_1_fu_682_p3) + unsigned(p_Result_s_fu_570_p3));
    add_ln232_5_fu_744_p2 <= std_logic_vector(unsigned(trunc_ln674_3_fu_700_p1) + unsigned(tmp_21_fu_728_p4));
    add_ln232_fu_704_p2 <= std_logic_vector(unsigned(tmp_20_fu_690_p4) + unsigned(trunc_ln674_3_fu_700_p1));
    add_ln414_8_fu_798_p2 <= std_logic_vector(unsigned(add_ln414_9_fu_794_p2) + unsigned(ret_V_10_reg_820));
    add_ln414_9_fu_794_p2 <= std_logic_vector(unsigned(ret_V_reg_815) + unsigned(t1_V_reg_825));
    add_ln414_fu_790_p2 <= std_logic_vector(unsigned(tmp_23_reg_841) + unsigned(t1_V_reg_825));
        ap_block_pp0_stage0 <= not((ap_const_boolean_1 = ap_const_boolean_1));
        ap_block_pp0_stage0_11001 <= not((ap_const_boolean_1 = ap_const_boolean_1));
        ap_block_state1_pp0_stage0_iter0 <= not((ap_const_boolean_1 = ap_const_boolean_1));
        ap_block_state2_pp0_stage0_iter1 <= not((ap_const_boolean_1 = ap_const_boolean_1));
    ap_return <= (((((tmp_24_reg_846 & add_ln414_fu_790_p2) & trunc_ln312_reg_851) & add_ln414_8_fu_798_p2) & new_w_V_reg_831) & tmp_22_reg_836);
    new_w_V_fu_750_p2 <= std_logic_vector(unsigned(add_ln232_5_fu_744_p2) + unsigned(add_ln232_4_fu_738_p2));
    p_Result_1_fu_682_p3 <= (temp0_V_3_fu_598_p2 & ret_V_12_fu_676_p2);
    p_Result_s_fu_570_p3 <= (temp0_V_2_fu_486_p2 & ret_V_11_fu_564_p2);
    ret_V_10_fu_460_p2 <= (ret_V_9_fu_454_p2 or ret_V_7_fu_442_p2);
    ret_V_11_fu_564_p2 <= (xor_ln1545_7_fu_558_p2 xor temp2_V_2_fu_540_p3);
    ret_V_12_fu_676_p2 <= (xor_ln1545_10_fu_670_p2 xor temp2_V_3_fu_652_p3);
    ret_V_3_fu_378_p2 <= (xor_ln1545_2_fu_372_p2 xor temp1_V_1_fu_336_p3);
    ret_V_4_fu_404_p2 <= (z_V_fu_394_p4 xor y_V_fu_384_p4);
    ret_V_5_fu_410_p2 <= (x_V_1_fu_278_p4 and ret_V_4_fu_404_p2);
    ret_V_6_fu_416_p2 <= (z_V_fu_394_p4 xor ret_V_5_fu_410_p2);
    ret_V_7_fu_442_p2 <= (y_V_1_fu_422_p4 and x_V_fu_196_p1);
    ret_V_8_fu_448_p2 <= (y_V_1_fu_422_p4 or x_V_fu_196_p1);
    ret_V_9_fu_454_p2 <= (z_V_1_fu_432_p4 and ret_V_8_fu_448_p2);
    ret_V_fu_272_p2 <= (xor_ln1545_fu_266_p2 xor temp1_V_fu_236_p3);
    t1_V_fu_722_p2 <= std_logic_vector(unsigned(add_ln232_2_fu_716_p2) + unsigned(add_ln232_fu_704_p2));
    temp0_V_1_fu_308_p3 <= (tmp_1_fu_298_p4 & tmp_9_fu_288_p4);
    temp0_V_2_fu_486_p2 <= (tmp_8_fu_476_p4 xor tmp_6_fu_466_p4);
    temp0_V_3_fu_598_p2 <= (tmp_15_fu_588_p4 xor tmp_14_fu_578_p4);
    temp0_V_fu_214_p3 <= (trunc_ln674_fu_210_p1 & tmp_fu_200_p4);
    temp1_V_1_fu_336_p3 <= (tmp_3_fu_326_p4 & tmp_2_fu_316_p4);
    temp1_V_2_fu_512_p3 <= (tmp_11_fu_502_p4 & tmp_10_fu_492_p4);
    temp1_V_3_fu_624_p3 <= (tmp_17_fu_614_p4 & tmp_16_fu_604_p4);
    temp1_V_fu_236_p3 <= (trunc_ln674_1_fu_232_p1 & tmp_5_fu_222_p4);
    temp2_V_1_fu_364_p3 <= (tmp_s_fu_354_p4 & tmp_4_fu_344_p4);
    temp2_V_2_fu_540_p3 <= (tmp_13_fu_530_p4 & tmp_12_fu_520_p4);
    temp2_V_3_fu_652_p3 <= (tmp_19_fu_642_p4 & tmp_18_fu_632_p4);
    temp2_V_fu_258_p3 <= (trunc_ln674_2_fu_254_p1 & tmp_7_fu_244_p4);
    temp3_V_1_fu_660_p4 <= rx_w(479 downto 458);
    temp3_V_fu_548_p4 <= rx_w(63 downto 35);
    tmp_10_fu_492_p4 <= rx_w(63 downto 39);
    tmp_11_fu_502_p4 <= rx_w(35 downto 32);
    tmp_12_fu_520_p4 <= rx_w(63 downto 50);
    tmp_13_fu_530_p4 <= rx_w(46 downto 32);
    tmp_14_fu_578_p4 <= rx_w(464 downto 455);
    tmp_15_fu_588_p4 <= rx_w(466 downto 457);
    tmp_16_fu_604_p4 <= rx_w(479 downto 465);
    tmp_17_fu_614_p4 <= rx_w(454 downto 448);
    tmp_18_fu_632_p4 <= rx_w(479 downto 467);
    tmp_19_fu_642_p4 <= rx_w(456 downto 448);
    tmp_1_fu_298_p4 <= rx_state(133 downto 128);
    tmp_20_fu_690_p4 <= rx_state(255 downto 224);
    tmp_21_fu_728_p4 <= rx_w(319 downto 288);
    tmp_2_fu_316_p4 <= rx_state(159 downto 139);
    tmp_3_fu_326_p4 <= rx_state(138 downto 128);
    tmp_4_fu_344_p4 <= rx_state(159 downto 153);
    tmp_5_fu_222_p4 <= rx_state(31 downto 13);
    tmp_6_fu_466_p4 <= rx_w(38 downto 36);
    tmp_7_fu_244_p4 <= rx_state(31 downto 22);
    tmp_8_fu_476_p4 <= rx_w(49 downto 47);
    tmp_9_fu_288_p4 <= rx_state(159 downto 134);
    tmp_fu_200_p4 <= rx_state(31 downto 2);
    tmp_s_fu_354_p4 <= rx_state(152 downto 128);
    trunc_ln312_fu_786_p1 <= rx_state(96 - 1 downto 0);
    trunc_ln674_1_fu_232_p1 <= rx_state(13 - 1 downto 0);
    trunc_ln674_2_fu_254_p1 <= rx_state(22 - 1 downto 0);
    trunc_ln674_3_fu_700_p1 <= rx_w(32 - 1 downto 0);
    trunc_ln674_fu_210_p1 <= rx_state(2 - 1 downto 0);
    x_V_1_fu_278_p4 <= rx_state(159 downto 128);
    x_V_fu_196_p1 <= rx_state(32 - 1 downto 0);
    xor_ln1545_10_fu_670_p2 <= (temp3_V_1_fu_660_p4 xor temp1_V_3_fu_624_p3);
    xor_ln1545_2_fu_372_p2 <= (temp2_V_1_fu_364_p3 xor temp0_V_1_fu_308_p3);
    xor_ln1545_7_fu_558_p2 <= (temp3_V_fu_548_p4 xor temp1_V_2_fu_512_p3);
    xor_ln1545_fu_266_p2 <= (temp2_V_fu_258_p3 xor temp0_V_fu_214_p3);
    y_V_1_fu_422_p4 <= rx_state(63 downto 32);
    y_V_fu_384_p4 <= rx_state(191 downto 160);
    z_V_1_fu_432_p4 <= rx_state(95 downto 64);
    z_V_fu_394_p4 <= rx_state(223 downto 192);
end behav;
