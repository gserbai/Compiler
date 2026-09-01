; ModuleID = "gencode-test-008.tpp"
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
  store i32 10, i32* @"n"
  store i32 0, i32* @"soma"
  br label %"repeat.body"
repeat.body:
  %".5" = load i32, i32* @"soma"
  %".6" = load i32, i32* @"n"
  %".7" = add i32 %".5", %".6"
  store i32 %".7", i32* @"soma"
  %".9" = load i32, i32* @"n"
  %".10" = sub i32 %".9", 1
  store i32 %".10", i32* @"n"
  %".12" = load i32, i32* @"n"
  %".13" = icmp eq i32 %".12", 0
  br i1 %".13", label %"repeat.end", label %"repeat.body"
repeat.end:
  %".15" = load i32, i32* @"soma"
  store i32 %".15", i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}
