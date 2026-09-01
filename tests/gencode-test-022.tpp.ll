; ModuleID = "gencode-test-022.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

define i32 @"maiorde2"(i32 %"x", i32 %"y")
{
entry:
  %"retval" = alloca i32
  %"x.1" = alloca i32
  store i32 %"x", i32* %"x.1"
  %"y.1" = alloca i32
  store i32 %"y", i32* %"y.1"
  %".6" = load i32, i32* %"x.1"
  %".7" = load i32, i32* %"y.1"
  %".8" = icmp sgt i32 %".6", %".7"
  br i1 %".8", label %"if.then", label %"if.end"
if.then:
  %".10" = load i32, i32* %"x.1"
  store i32 %".10", i32* %"retval"
  br label %"exit"
if.end:
  %".13" = load i32, i32* %"y.1"
  store i32 %".13", i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

define i32 @"maiorde4"(i32 %"a", i32 %"b", i32 %"c", i32 %"d")
{
entry:
  %"retval" = alloca i32
  %"a.1" = alloca i32
  store i32 %"a", i32* %"a.1"
  %"b.1" = alloca i32
  store i32 %"b", i32* %"b.1"
  %"c.1" = alloca i32
  store i32 %"c", i32* %"c.1"
  %"d.1" = alloca i32
  store i32 %"d", i32* %"d.1"
  %".10" = load i32, i32* %"a.1"
  %".11" = load i32, i32* %"b.1"
  %".12" = call i32 @"maiorde2"(i32 %".10", i32 %".11")
  %".13" = load i32, i32* %"c.1"
  %".14" = load i32, i32* %"d.1"
  %".15" = call i32 @"maiorde2"(i32 %".13", i32 %".14")
  %".16" = call i32 @"maiorde2"(i32 %".12", i32 %".15")
  store i32 %".16", i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

define i32 @"main"()
{
entry:
  %"retval" = alloca i32
  %"A" = alloca i32
  %"B" = alloca i32
  %"C" = alloca i32
  %"D" = alloca i32
  %".2" = getelementptr inbounds [3 x i8], [3 x i8]* @"fmt_scan_int_0", i32 0, i32 0
  %".3" = call i32 (i8*, ...) @"scanf"(i8* %".2", i32* %"A")
  %".4" = getelementptr inbounds [3 x i8], [3 x i8]* @"fmt_scan_int_1", i32 0, i32 0
  %".5" = call i32 (i8*, ...) @"scanf"(i8* %".4", i32* %"B")
  %".6" = getelementptr inbounds [3 x i8], [3 x i8]* @"fmt_scan_int_2", i32 0, i32 0
  %".7" = call i32 (i8*, ...) @"scanf"(i8* %".6", i32* %"C")
  %".8" = getelementptr inbounds [3 x i8], [3 x i8]* @"fmt_scan_int_3", i32 0, i32 0
  %".9" = call i32 (i8*, ...) @"scanf"(i8* %".8", i32* %"D")
  %".10" = load i32, i32* %"A"
  %".11" = load i32, i32* %"B"
  %".12" = load i32, i32* %"C"
  %".13" = load i32, i32* %"D"
  %".14" = call i32 @"maiorde4"(i32 %".10", i32 %".11", i32 %".12", i32 %".13")
  %".15" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_4", i32 0, i32 0
  %".16" = call i32 (i8*, ...) @"printf"(i8* %".15", i32 %".14")
  store i32 0, i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

@"fmt_scan_int_0" = internal constant [3 x i8] c"%d\00"
@"fmt_scan_int_1" = internal constant [3 x i8] c"%d\00"
@"fmt_scan_int_2" = internal constant [3 x i8] c"%d\00"
@"fmt_scan_int_3" = internal constant [3 x i8] c"%d\00"
@"fmt_print_int_4" = internal constant [4 x i8] c"%d\0a\00"