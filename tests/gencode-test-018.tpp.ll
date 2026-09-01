; ModuleID = "gencode-test-018.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

@"n" = common global i32 0, align 4
define i32 @"fatorial"(i32 %"n")
{
entry:
  %"retval" = alloca i32
  %"n.1" = alloca i32
  store i32 %"n", i32* %"n.1"
  %"fat" = alloca i32
  %".4" = load i32, i32* %"n.1"
  %".5" = icmp sgt i32 %".4", 0
  br i1 %".5", label %"if.then", label %"if.else"
if.then:
  store i32 1, i32* %"fat"
  br label %"repeat.body"
if.else:
  store i32 0, i32* %"retval"
  br label %"exit"
if.end:
  store i32 0, i32* %"retval"
  br label %"exit"
repeat.body:
  %".9" = load i32, i32* %"fat"
  %".10" = load i32, i32* %"n.1"
  %".11" = mul i32 %".9", %".10"
  store i32 %".11", i32* %"fat"
  %".13" = load i32, i32* %"n.1"
  %".14" = sub i32 %".13", 1
  store i32 %".14", i32* %"n.1"
  %".16" = load i32, i32* %"n.1"
  %".17" = icmp eq i32 %".16", 0
  br i1 %".17", label %"repeat.end", label %"repeat.body"
repeat.end:
  %".19" = load i32, i32* %"fat"
  store i32 %".19", i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

define i32 @"main"()
{
entry:
  %"retval" = alloca i32
  %".2" = getelementptr inbounds [3 x i8], [3 x i8]* @"fmt_scan_int_0", i32 0, i32 0
  %".3" = call i32 (i8*, ...) @"scanf"(i8* %".2", i32* @"n")
  %".4" = load i32, i32* @"n"
  %".5" = call i32 @"fatorial"(i32 %".4")
  %".6" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_1", i32 0, i32 0
  %".7" = call i32 (i8*, ...) @"printf"(i8* %".6", i32 %".5")
  store i32 0, i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

@"fmt_scan_int_0" = internal constant [3 x i8] c"%d\00"
@"fmt_print_int_1" = internal constant [4 x i8] c"%d\0a\00"