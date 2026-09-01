; ModuleID = "gencode-test-031.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

@"i" = common global i32 0, align 4
@"j" = common global i32 0, align 4
@"x" = common global i32 0, align 4
@"tam" = common global i32 0, align 4
@"vet" = common global [11 x i32] zeroinitializer, align 4
define void @"insert_sort"()
{
entry:
  store i32 2, i32* @"i"
  br label %"repeat.body"
repeat.body:
  %".4" = load i32, i32* @"i"
  %".5" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 %".4"
  %".6" = load i32, i32* %".5"
  store i32 %".6", i32* @"x"
  %".8" = load i32, i32* @"i"
  %".9" = sub i32 %".8", 1
  store i32 %".9", i32* @"j"
  %".11" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 0
  %".12" = load i32, i32* @"x"
  store i32 %".12", i32* %".11"
  %".14" = load i32, i32* @"x"
  %".15" = load i32, i32* @"j"
  %".16" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 %".15"
  %".17" = load i32, i32* %".16"
  %".18" = icmp slt i32 %".14", %".17"
  br i1 %".18", label %"if.then", label %"if.end"
repeat.end:
  br label %"exit"
if.then:
  br label %"repeat.body.1"
if.end:
  %".38" = load i32, i32* @"j"
  %".39" = add i32 %".38", 1
  %".40" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 %".39"
  %".41" = load i32, i32* @"x"
  store i32 %".41", i32* %".40"
  %".43" = load i32, i32* @"i"
  %".44" = add i32 %".43", 1
  store i32 %".44", i32* @"i"
  %".46" = load i32, i32* @"i"
  %".47" = load i32, i32* @"tam"
  %".48" = icmp sgt i32 %".46", %".47"
  br i1 %".48", label %"repeat.end", label %"repeat.body"
repeat.body.1:
  %".21" = load i32, i32* @"j"
  %".22" = add i32 %".21", 1
  %".23" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 %".22"
  %".24" = load i32, i32* @"j"
  %".25" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 %".24"
  %".26" = load i32, i32* %".25"
  store i32 %".26", i32* %".23"
  %".28" = load i32, i32* @"j"
  %".29" = sub i32 %".28", 1
  store i32 %".29", i32* @"j"
  %".31" = load i32, i32* @"x"
  %".32" = load i32, i32* @"j"
  %".33" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 %".32"
  %".34" = load i32, i32* %".33"
  %".35" = icmp sge i32 %".31", %".34"
  br i1 %".35", label %"repeat.end.1", label %"repeat.body.1"
repeat.end.1:
  br label %"if.end"
exit:
  ret void
}

define void @"printArray"()
{
entry:
  %"p" = alloca i32
  store i32 1, i32* %"p"
  br label %"repeat.body"
repeat.body:
  %".4" = load i32, i32* %"p"
  %".5" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 %".4"
  %".6" = load i32, i32* %".5"
  %".7" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_0", i32 0, i32 0
  %".8" = call i32 (i8*, ...) @"printf"(i8* %".7", i32 %".6")
  %".9" = load i32, i32* %"p"
  %".10" = add i32 %".9", 1
  store i32 %".10", i32* %"p"
  %".12" = load i32, i32* %"p"
  %".13" = load i32, i32* @"tam"
  %".14" = icmp sgt i32 %".12", %".13"
  br i1 %".14", label %"repeat.end", label %"repeat.body"
repeat.end:
  br label %"exit"
exit:
  ret void
}

define i32 @"main"()
{
entry:
  %"retval" = alloca i32
  store i32 10, i32* @"tam"
  %".3" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 1
  store i32 5, i32* %".3"
  %".5" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 2
  store i32 3, i32* %".5"
  %".7" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 3
  store i32 2, i32* %".7"
  %".9" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 4
  store i32 4, i32* %".9"
  %".11" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 5
  store i32 7, i32* %".11"
  %".13" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 6
  store i32 1, i32* %".13"
  %".15" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 7
  store i32 0, i32* %".15"
  %".17" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 8
  store i32 6, i32* %".17"
  %".19" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 9
  store i32 9, i32* %".19"
  %".21" = getelementptr [11 x i32], [11 x i32]* @"vet", i32 0, i32 10
  store i32 8, i32* %".21"
  call void @"insert_sort"()
  call void @"printArray"()
  store i32 0, i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

@"fmt_print_int_0" = internal constant [4 x i8] c"%d\0a\00"