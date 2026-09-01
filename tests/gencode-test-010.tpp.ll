; ModuleID = "gencode-test-010.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

define i32 @"main"()
{
entry:
  %"retval" = alloca i32
  %"a" = alloca i32
  %"b" = alloca i32
  %"c" = alloca i32
  %".2" = getelementptr inbounds [3 x i8], [3 x i8]* @"fmt_scan_int_0", i32 0, i32 0
  %".3" = call i32 (i8*, ...) @"scanf"(i8* %".2", i32* %"a")
  %".4" = getelementptr inbounds [3 x i8], [3 x i8]* @"fmt_scan_int_1", i32 0, i32 0
  %".5" = call i32 (i8*, ...) @"scanf"(i8* %".4", i32* %"b")
  %".6" = load i32, i32* %"a"
  %".7" = load i32, i32* %"b"
  %".8" = add i32 %".6", %".7"
  store i32 %".8", i32* %"c"
  %".10" = load i32, i32* %"c"
  %".11" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_2", i32 0, i32 0
  %".12" = call i32 (i8*, ...) @"printf"(i8* %".11", i32 %".10")
  store i32 0, i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

@"fmt_scan_int_0" = internal constant [3 x i8] c"%d\00"
@"fmt_scan_int_1" = internal constant [3 x i8] c"%d\00"
@"fmt_print_int_2" = internal constant [4 x i8] c"%d\0a\00"