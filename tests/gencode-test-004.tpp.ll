; ModuleID = "gencode-test-004.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

@"a" = common global i32 0, align 4
@"b" = common global i32 0, align 4
define i32 @"main"()
{
entry:
  %"retval" = alloca i32
  %"c" = alloca i32
  store i32 10, i32* @"a"
  store i32 20, i32* @"b"
  %".4" = load i32, i32* @"a"
  %".5" = load i32, i32* @"b"
  %".6" = add i32 %".4", %".5"
  store i32 %".6", i32* %"c"
  %".8" = load i32, i32* %"c"
  store i32 %".8", i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}
