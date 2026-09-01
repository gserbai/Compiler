; ModuleID = "gencode-test-024.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

define i32 @"func"(i32 %"p1", i32 %"p2")
{
entry:
  %"retval" = alloca i32
  %"p1.1" = alloca i32
  store i32 %"p1", i32* %"p1.1"
  %"p2.1" = alloca i32
  store i32 %"p2", i32* %"p2.1"
  %"r" = alloca i32
  %".6" = load i32, i32* %"p1.1"
  %".7" = load i32, i32* %"p2.1"
  %".8" = add i32 %".6", %".7"
  store i32 %".8", i32* %"r"
  %".10" = load i32, i32* %"r"
  store i32 %".10", i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

define i32 @"main"()
{
entry:
  %"retval" = alloca i32
  %"x" = alloca i32
  %".2" = call i32 @"func"(i32 1, i32 2)
  store i32 %".2", i32* %"x"
  %".4" = load i32, i32* %"x"
  %".5" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_0", i32 0, i32 0
  %".6" = call i32 (i8*, ...) @"printf"(i8* %".5", i32 %".4")
  store i32 0, i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

@"fmt_print_int_0" = internal constant [4 x i8] c"%d\0a\00"