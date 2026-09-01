; ModuleID = "gencode-test-019.tpp"
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
  %".4" = icmp sge i32 %".3", 5
  %".5" = load i32, i32* @"a"
  %".6" = icmp sle i32 %".5", 20
  %".7" = and i1 %".4", %".6"
  br i1 %".7", label %"if.then", label %"if.else"
if.then:
  store i32 50, i32* %"b"
  br label %"if.end"
if.else:
  store i32 100, i32* %"b"
  br label %"if.end"
if.end:
  %".13" = load i32, i32* %"b"
  store i32 %".13", i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}
