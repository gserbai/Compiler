; ModuleID = "gencode-test-003.tpp"
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
  store i32 10, i32* @"a"
  %".3" = load i32, i32* @"a"
  store i32 %".3", i32* %"b"
  %".5" = load i32, i32* %"b"
  store i32 %".5", i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}
