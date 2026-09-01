; ModuleID = "gencode-test-015.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

define i32 @"soma"(i32 %"x", i32 %"y")
{
entry:
  %"retval" = alloca i32
  %"x.1" = alloca i32
  store i32 %"x", i32* %"x.1"
  %"y.1" = alloca i32
  store i32 %"y", i32* %"y.1"
  %".6" = load i32, i32* %"x.1"
  %".7" = load i32, i32* %"y.1"
  %".8" = add i32 %".6", %".7"
  store i32 %".8", i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

define i32 @"sub"(i32 %"z", i32 %"t")
{
entry:
  %"retval" = alloca i32
  %"z.1" = alloca i32
  store i32 %"z", i32* %"z.1"
  %"t.1" = alloca i32
  store i32 %"t", i32* %"t.1"
  %".6" = load i32, i32* %"z.1"
  %".7" = load i32, i32* %"t.1"
  %".8" = sub i32 %".6", %".7"
  store i32 %".8", i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

define i32 @"main"()
{
entry:
  %"retval" = alloca i32
  %"a" = alloca i32
  %"b" = alloca i32
  %"c" = alloca i32
  %"i" = alloca i32
  store i32 0, i32* %"i"
  br label %"repeat.body"
repeat.body:
  %".4" = getelementptr inbounds [3 x i8], [3 x i8]* @"fmt_scan_int_0", i32 0, i32 0
  %".5" = call i32 (i8*, ...) @"scanf"(i8* %".4", i32* %"a")
  %".6" = getelementptr inbounds [3 x i8], [3 x i8]* @"fmt_scan_int_1", i32 0, i32 0
  %".7" = call i32 (i8*, ...) @"scanf"(i8* %".6", i32* %"b")
  %".8" = load i32, i32* %"a"
  %".9" = load i32, i32* %"b"
  %".10" = call i32 @"soma"(i32 %".8", i32 %".9")
  %".11" = load i32, i32* %"a"
  %".12" = load i32, i32* %"b"
  %".13" = call i32 @"sub"(i32 %".11", i32 %".12")
  %".14" = call i32 @"soma"(i32 %".10", i32 %".13")
  store i32 %".14", i32* %"c"
  %".16" = load i32, i32* %"c"
  %".17" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_2", i32 0, i32 0
  %".18" = call i32 (i8*, ...) @"printf"(i8* %".17", i32 %".16")
  %".19" = load i32, i32* %"i"
  %".20" = add i32 %".19", 1
  store i32 %".20", i32* %"i"
  %".22" = load i32, i32* %"i"
  %".23" = icmp eq i32 %".22", 5
  br i1 %".23", label %"repeat.end", label %"repeat.body"
repeat.end:
  store i32 0, i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

@"fmt_scan_int_0" = internal constant [3 x i8] c"%d\00"
@"fmt_scan_int_1" = internal constant [3 x i8] c"%d\00"
@"fmt_print_int_2" = internal constant [4 x i8] c"%d\0a\00"