; ModuleID = "gencode-test-020.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

@"a" = common global i32 0, align 4
define i32 @"main"()
{
entry:
  %"retval" = alloca i32
  %"b" = alloca i32
  %".2" = getelementptr inbounds [3 x i8], [3 x i8]* @"fmt_scan_int_0", i32 0, i32 0
  %".3" = call i32 (i8*, ...) @"scanf"(i8* %".2", i32* @"a")
  %".4" = load i32, i32* @"a"
  %".5" = icmp sge i32 %".4", 5
  %".6" = load i32, i32* @"a"
  %".7" = icmp sle i32 %".6", 20
  %".8" = and i1 %".5", %".7"
  br i1 %".8", label %"if.then", label %"if.else"
if.then:
  store i32 50, i32* %"b"
  br label %"if.end"
if.else:
  store i32 100, i32* %"b"
  br label %"if.end"
if.end:
  %".14" = load i32, i32* %"b"
  %".15" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_1", i32 0, i32 0
  %".16" = call i32 (i8*, ...) @"printf"(i8* %".15", i32 %".14")
  store i32 0, i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

@"fmt_scan_int_0" = internal constant [3 x i8] c"%d\00"
@"fmt_print_int_1" = internal constant [4 x i8] c"%d\0a\00"