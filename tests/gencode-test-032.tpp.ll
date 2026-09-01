; ModuleID = "gencode-test-032.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

@"v" = common global [10 x i32] zeroinitializer, align 4
@"tam" = common global i32 0, align 4
define i32 @"partition"(i32 %"e", i32 %"d")
{
entry:
  %"retval" = alloca i32
  %"e.1" = alloca i32
  store i32 %"e", i32* %"e.1"
  %"d.1" = alloca i32
  store i32 %"d", i32* %"d.1"
  %"pivo" = alloca i32
  %"i" = alloca i32
  %"j" = alloca i32
  %"aux" = alloca i32
  %".6" = load i32, i32* %"d.1"
  %".7" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 %".6"
  %".8" = load i32, i32* %".7"
  store i32 %".8", i32* %"pivo"
  %".10" = load i32, i32* %"e.1"
  %".11" = sub i32 %".10", 1
  store i32 %".11", i32* %"i"
  %".13" = load i32, i32* %"e.1"
  store i32 %".13", i32* %"j"
  br label %"repeat.body"
repeat.body:
  %".16" = load i32, i32* %"j"
  %".17" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 %".16"
  %".18" = load i32, i32* %".17"
  %".19" = load i32, i32* %"pivo"
  %".20" = icmp sle i32 %".18", %".19"
  br i1 %".20", label %"if.then", label %"if.end"
repeat.end:
  %".47" = load i32, i32* %"i"
  %".48" = add i32 %".47", 1
  %".49" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 %".48"
  %".50" = load i32, i32* %".49"
  store i32 %".50", i32* %"aux"
  %".52" = load i32, i32* %"i"
  %".53" = add i32 %".52", 1
  %".54" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 %".53"
  %".55" = load i32, i32* %"d.1"
  %".56" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 %".55"
  %".57" = load i32, i32* %".56"
  store i32 %".57", i32* %".54"
  %".59" = load i32, i32* %"d.1"
  %".60" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 %".59"
  %".61" = load i32, i32* %"aux"
  store i32 %".61", i32* %".60"
  %".63" = load i32, i32* %"i"
  %".64" = add i32 %".63", 1
  store i32 %".64", i32* %"retval"
  br label %"exit"
if.then:
  %".22" = load i32, i32* %"i"
  %".23" = add i32 %".22", 1
  store i32 %".23", i32* %"i"
  %".25" = load i32, i32* %"i"
  %".26" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 %".25"
  %".27" = load i32, i32* %".26"
  store i32 %".27", i32* %"aux"
  %".29" = load i32, i32* %"i"
  %".30" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 %".29"
  %".31" = load i32, i32* %"j"
  %".32" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 %".31"
  %".33" = load i32, i32* %".32"
  store i32 %".33", i32* %".30"
  %".35" = load i32, i32* %"j"
  %".36" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 %".35"
  %".37" = load i32, i32* %"aux"
  store i32 %".37", i32* %".36"
  br label %"if.end"
if.end:
  %".40" = load i32, i32* %"j"
  %".41" = add i32 %".40", 1
  store i32 %".41", i32* %"j"
  %".43" = load i32, i32* %"j"
  %".44" = load i32, i32* %"d.1"
  %".45" = icmp eq i32 %".43", %".44"
  br i1 %".45", label %"repeat.end", label %"repeat.body"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

define void @"quick"(i32 %"e", i32 %"d")
{
entry:
  %"e.1" = alloca i32
  store i32 %"e", i32* %"e.1"
  %"d.1" = alloca i32
  store i32 %"d", i32* %"d.1"
  %"p" = alloca i32
  %".6" = load i32, i32* %"e.1"
  %".7" = load i32, i32* %"d.1"
  %".8" = icmp slt i32 %".6", %".7"
  br i1 %".8", label %"if.then", label %"if.end"
if.then:
  %".10" = load i32, i32* %"e.1"
  %".11" = load i32, i32* %"d.1"
  %".12" = call i32 @"partition"(i32 %".10", i32 %".11")
  store i32 %".12", i32* %"p"
  %".14" = load i32, i32* %"e.1"
  %".15" = load i32, i32* %"p"
  %".16" = sub i32 %".15", 1
  call void @"quick"(i32 %".14", i32 %".16")
  %".18" = load i32, i32* %"p"
  %".19" = add i32 %".18", 1
  %".20" = load i32, i32* %"d.1"
  call void @"quick"(i32 %".19", i32 %".20")
  br label %"if.end"
if.end:
  br label %"exit"
exit:
  ret void
}

define void @"printArray"()
{
entry:
  %"i" = alloca i32
  store i32 0, i32* %"i"
  br label %"repeat.body"
repeat.body:
  %".4" = load i32, i32* %"i"
  %".5" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 %".4"
  %".6" = load i32, i32* %".5"
  %".7" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_0", i32 0, i32 0
  %".8" = call i32 (i8*, ...) @"printf"(i8* %".7", i32 %".6")
  %".9" = load i32, i32* %"i"
  %".10" = add i32 %".9", 1
  store i32 %".10", i32* %"i"
  %".12" = load i32, i32* %"i"
  %".13" = load i32, i32* @"tam"
  %".14" = icmp eq i32 %".12", %".13"
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
  %".3" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 0
  store i32 5, i32* %".3"
  %".5" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 1
  store i32 3, i32* %".5"
  %".7" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 2
  store i32 2, i32* %".7"
  %".9" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 3
  store i32 4, i32* %".9"
  %".11" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 4
  store i32 7, i32* %".11"
  %".13" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 5
  store i32 1, i32* %".13"
  %".15" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 6
  store i32 0, i32* %".15"
  %".17" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 7
  store i32 6, i32* %".17"
  %".19" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 8
  store i32 9, i32* %".19"
  %".21" = getelementptr [10 x i32], [10 x i32]* @"v", i32 0, i32 9
  store i32 8, i32* %".21"
  call void @"quick"(i32 0, i32 9)
  call void @"printArray"()
  store i32 0, i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

@"fmt_print_int_0" = internal constant [4 x i8] c"%d\0a\00"