; ModuleID = "gencode-test-013.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

define i32 @"soma"(i32 %"a", i32 %"b")
{
entry:
  %"retval" = alloca i32
  %"a.1" = alloca i32
  store i32 %"a", i32* %"a.1"
  %"b.1" = alloca i32
  store i32 %"b", i32* %"b.1"
  %".6" = load i32, i32* %"a.1"
  %".7" = load i32, i32* %"b.1"
  %".8" = add i32 %".6", %".7"
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
  store i32 %".10", i32* %"c"
  %".12" = load i32, i32* %"c"
  %".13" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_2", i32 0, i32 0
  %".14" = call i32 (i8*, ...) @"printf"(i8* %".13", i32 %".12")
  %".15" = load i32, i32* %"i"
  %".16" = add i32 %".15", 1
  store i32 %".16", i32* %"i"
  %".18" = load i32, i32* %"i"
  %".19" = icmp eq i32 %".18", 5
  br i1 %".19", label %"repeat.end", label %"repeat.body"
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