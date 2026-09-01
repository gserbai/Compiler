; ModuleID = "gencode-test-016.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

@"A" = common global [1024 x i32] zeroinitializer, align 4
@"B" = common global [1024 x i32] zeroinitializer, align 4
define i32 @"main"()
{
entry:
  %"retval" = alloca i32
  %"a" = alloca i32
  %"i" = alloca i32
  store i32 0, i32* %"i"
  br label %"repeat.body"
repeat.body:
  %".4" = getelementptr inbounds [3 x i8], [3 x i8]* @"fmt_scan_int_0", i32 0, i32 0
  %".5" = call i32 (i8*, ...) @"scanf"(i8* %".4", i32* %"a")
  %".6" = load i32, i32* %"i"
  %".7" = getelementptr [1024 x i32], [1024 x i32]* @"A", i32 0, i32 %".6"
  %".8" = load i32, i32* %"a"
  store i32 %".8", i32* %".7"
  %".10" = load i32, i32* %"i"
  %".11" = add i32 %".10", 1
  store i32 %".11", i32* %"i"
  %".13" = load i32, i32* %"i"
  %".14" = icmp eq i32 %".13", 1024
  br i1 %".14", label %"repeat.end", label %"repeat.body"
repeat.end:
  store i32 0, i32* %"i"
  br label %"repeat.body.1"
repeat.body.1:
  %".18" = load i32, i32* %"i"
  %".19" = sub i32 1023, %".18"
  %".20" = getelementptr [1024 x i32], [1024 x i32]* @"B", i32 0, i32 %".19"
  %".21" = load i32, i32* %"i"
  %".22" = getelementptr [1024 x i32], [1024 x i32]* @"A", i32 0, i32 %".21"
  %".23" = load i32, i32* %".22"
  store i32 %".23", i32* %".20"
  %".25" = load i32, i32* %"i"
  %".26" = add i32 %".25", 1
  store i32 %".26", i32* %"i"
  %".28" = load i32, i32* %"i"
  %".29" = icmp eq i32 %".28", 1024
  br i1 %".29", label %"repeat.end.1", label %"repeat.body.1"
repeat.end.1:
  store i32 0, i32* %"i"
  br label %"repeat.body.2"
repeat.body.2:
  %".33" = load i32, i32* %"i"
  %".34" = getelementptr [1024 x i32], [1024 x i32]* @"B", i32 0, i32 %".33"
  %".35" = load i32, i32* %".34"
  %".36" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_1", i32 0, i32 0
  %".37" = call i32 (i8*, ...) @"printf"(i8* %".36", i32 %".35")
  %".38" = load i32, i32* %"i"
  %".39" = add i32 %".38", 1
  store i32 %".39", i32* %"i"
  %".41" = load i32, i32* %"i"
  %".42" = icmp eq i32 %".41", 1024
  br i1 %".42", label %"repeat.end.2", label %"repeat.body.2"
repeat.end.2:
  store i32 0, i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

@"fmt_scan_int_0" = internal constant [3 x i8] c"%d\00"
@"fmt_print_int_1" = internal constant [4 x i8] c"%d\0a\00"