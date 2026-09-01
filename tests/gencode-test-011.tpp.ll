; ModuleID = "gencode-test-011.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

@"n" = common global i32 0, align 4
@"soma" = common global i32 0, align 4
define i32 @"main"()
{
entry:
  %"retval" = alloca i32
  %".2" = getelementptr inbounds [3 x i8], [3 x i8]* @"fmt_scan_int_0", i32 0, i32 0
  %".3" = call i32 (i8*, ...) @"scanf"(i8* %".2", i32* @"n")
  store i32 0, i32* @"soma"
  br label %"repeat.body"
repeat.body:
  %".6" = load i32, i32* @"soma"
  %".7" = load i32, i32* @"n"
  %".8" = add i32 %".6", %".7"
  store i32 %".8", i32* @"soma"
  %".10" = load i32, i32* @"n"
  %".11" = sub i32 %".10", 1
  store i32 %".11", i32* @"n"
  %".13" = load i32, i32* @"n"
  %".14" = icmp eq i32 %".13", 0
  br i1 %".14", label %"repeat.end", label %"repeat.body"
repeat.end:
  %".16" = load i32, i32* @"soma"
  %".17" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_1", i32 0, i32 0
  %".18" = call i32 (i8*, ...) @"printf"(i8* %".17", i32 %".16")
  store i32 0, i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

@"fmt_scan_int_0" = internal constant [3 x i8] c"%d\00"
@"fmt_print_int_1" = internal constant [4 x i8] c"%d\0a\00"