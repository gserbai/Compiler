; ModuleID = "gencode-test-007.tpp"
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
  store i32 25, i32* @"a"
  %".3" = load i32, i32* @"a"
  %".4" = icmp sgt i32 %".3", 5
  br i1 %".4", label %"if.then", label %"if.else"
if.then:
  %".6" = load i32, i32* @"a"
  %".7" = icmp slt i32 %".6", 20
  br i1 %".7", label %"if.then.1", label %"if.else.1"
if.else:
  store i32 0, i32* %"ret"
  br label %"if.end"
if.end:
  %".16" = load i32, i32* %"ret"
  store i32 %".16", i32* %"retval"
  br label %"exit"
if.then.1:
  store i32 1, i32* %"ret"
  br label %"if.end.1"
if.else.1:
  store i32 2, i32* %"ret"
  br label %"if.end.1"
if.end.1:
  br label %"if.end"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}
