; ModuleID = "gencode-test-009.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

define i32 @"main"()
{
entry:
  %"retval" = alloca i32
  %"x" = alloca i32
  %"y" = alloca double
  store i32 0, i32* %"x"
  store double              0x0, double* %"y"
  %".4" = getelementptr inbounds [3 x i8], [3 x i8]* @"fmt_scan_int_0", i32 0, i32 0
  %".5" = call i32 (i8*, ...) @"scanf"(i8* %".4", i32* %"x")
  %".6" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_scan_float_1", i32 0, i32 0
  %".7" = call i32 (i8*, ...) @"scanf"(i8* %".6", double* %"y")
  %".8" = load i32, i32* %"x"
  %".9" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_2", i32 0, i32 0
  %".10" = call i32 (i8*, ...) @"printf"(i8* %".9", i32 %".8")
  %".11" = load double, double* %"y"
  %".12" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_float_3", i32 0, i32 0
  %".13" = call i32 (i8*, ...) @"printf"(i8* %".12", double %".11")
  store i32 0, i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

@"fmt_scan_int_0" = internal constant [3 x i8] c"%d\00"
@"fmt_scan_float_1" = internal constant [4 x i8] c"%lf\00"
@"fmt_print_int_2" = internal constant [4 x i8] c"%d\0a\00"
@"fmt_print_float_3" = internal constant [4 x i8] c"%f\0a\00"