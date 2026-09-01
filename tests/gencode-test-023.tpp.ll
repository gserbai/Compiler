; ModuleID = "gencode-test-023.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

define i32 @"fibonacciRec"(i32 %"n")
{
entry:
  %"retval" = alloca i32
  %"n.1" = alloca i32
  store i32 %"n", i32* %"n.1"
  %".4" = load i32, i32* %"n.1"
  %".5" = icmp sle i32 %".4", 1
  br i1 %".5", label %"if.then", label %"if.else"
if.then:
  %".7" = load i32, i32* %"n.1"
  store i32 %".7", i32* %"retval"
  br label %"exit"
if.else:
  %".10" = load i32, i32* %"n.1"
  %".11" = sub i32 %".10", 1
  %".12" = call i32 @"fibonacciRec"(i32 %".11")
  %".13" = load i32, i32* %"n.1"
  %".14" = sub i32 %".13", 2
  %".15" = call i32 @"fibonacciRec"(i32 %".14")
  %".16" = add i32 %".12", %".15"
  store i32 %".16", i32* %"retval"
  br label %"exit"
if.end:
  store i32 0, i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

define i32 @"fibonacciIter"(i32 %"n")
{
entry:
  %"retval" = alloca i32
  %"n.1" = alloca i32
  store i32 %"n", i32* %"n.1"
  %"i" = alloca i32
  %"f" = alloca i32
  %"k" = alloca i32
  store i32 1, i32* %"i"
  store i32 0, i32* %"f"
  store i32 1, i32* %"k"
  br label %"repeat.body"
repeat.body:
  %".8" = load i32, i32* %"i"
  %".9" = load i32, i32* %"f"
  %".10" = add i32 %".8", %".9"
  store i32 %".10", i32* %"f"
  %".12" = load i32, i32* %"f"
  %".13" = load i32, i32* %"i"
  %".14" = sub i32 %".12", %".13"
  store i32 %".14", i32* %"i"
  %".16" = load i32, i32* %"k"
  %".17" = add i32 %".16", 1
  store i32 %".17", i32* %"k"
  %".19" = load i32, i32* %"k"
  %".20" = load i32, i32* %"n.1"
  %".21" = icmp sgt i32 %".19", %".20"
  br i1 %".21", label %"repeat.end", label %"repeat.body"
repeat.end:
  %".23" = load i32, i32* %"f"
  store i32 %".23", i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

define i32 @"main"()
{
entry:
  %"retval" = alloca i32
  %"n" = alloca i32
  %"i" = alloca i32
  %".2" = getelementptr inbounds [3 x i8], [3 x i8]* @"fmt_scan_int_0", i32 0, i32 0
  %".3" = call i32 (i8*, ...) @"scanf"(i8* %".2", i32* %"n")
  store i32 1, i32* %"i"
  br label %"repeat.body"
repeat.body:
  %".6" = load i32, i32* %"i"
  %".7" = call i32 @"fibonacciIter"(i32 %".6")
  %".8" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_1", i32 0, i32 0
  %".9" = call i32 (i8*, ...) @"printf"(i8* %".8", i32 %".7")
  %".10" = load i32, i32* %"i"
  %".11" = add i32 %".10", 1
  store i32 %".11", i32* %"i"
  %".13" = load i32, i32* %"i"
  %".14" = load i32, i32* %"n"
  %".15" = icmp sgt i32 %".13", %".14"
  br i1 %".15", label %"repeat.end", label %"repeat.body"
repeat.end:
  store i32 1, i32* %"i"
  br label %"repeat.body.1"
repeat.body.1:
  %".19" = load i32, i32* %"i"
  %".20" = call i32 @"fibonacciRec"(i32 %".19")
  %".21" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_2", i32 0, i32 0
  %".22" = call i32 (i8*, ...) @"printf"(i8* %".21", i32 %".20")
  %".23" = load i32, i32* %"i"
  %".24" = add i32 %".23", 1
  store i32 %".24", i32* %"i"
  %".26" = load i32, i32* %"i"
  %".27" = load i32, i32* %"n"
  %".28" = icmp sgt i32 %".26", %".27"
  br i1 %".28", label %"repeat.end.1", label %"repeat.body.1"
repeat.end.1:
  store i32 0, i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

@"fmt_scan_int_0" = internal constant [3 x i8] c"%d\00"
@"fmt_print_int_1" = internal constant [4 x i8] c"%d\0a\00"
@"fmt_print_int_2" = internal constant [4 x i8] c"%d\0a\00"