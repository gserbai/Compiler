; ModuleID = "gencode-test-006.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

@"a" = common global i32 0, align 4
define i32 @"main"()
{
entry:
  %"retval" = alloca i32
  %"ret" = alloca i32
  store i32 3, i32* @"a"
  %".3" = load i32, i32* @"a"
  %".4" = icmp sgt i32 %".3", 5
  br i1 %".4", label %"if.then", label %"if.else"
if.then:
  store i32 1, i32* %"ret"
  br label %"if.end"
if.else:
  store i32 2, i32* %"ret"
  br label %"if.end"
if.end:
  %".10" = load i32, i32* %"ret"
  store i32 %".10", i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}
