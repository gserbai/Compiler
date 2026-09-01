; ModuleID = "gencode-test-021.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

@"ano" = common global i32 0, align 4
define i32 @"modulo"(i32 %"numerador", i32 %"denominador")
{
entry:
  %"retval" = alloca i32
  %"numerador.1" = alloca i32
  store i32 %"numerador", i32* %"numerador.1"
  %"denominador.1" = alloca i32
  store i32 %"denominador", i32* %"denominador.1"
  %".6" = load i32, i32* %"numerador.1"
  %".7" = load i32, i32* %"denominador.1"
  %".8" = icmp slt i32 %".6", %".7"
  br i1 %".8", label %"if.then", label %"if.end"
if.then:
  %".10" = load i32, i32* %"numerador.1"
  store i32 %".10", i32* %"retval"
  br label %"exit"
if.end:
  br label %"repeat.body"
repeat.body:
  %".14" = load i32, i32* %"numerador.1"
  %".15" = load i32, i32* %"denominador.1"
  %".16" = sub i32 %".14", %".15"
  store i32 %".16", i32* %"numerador.1"
  %".18" = load i32, i32* %"numerador.1"
  %".19" = load i32, i32* %"denominador.1"
  %".20" = icmp sle i32 %".18", %".19"
  br i1 %".20", label %"repeat.end", label %"repeat.body"
repeat.end:
  %".22" = load i32, i32* %"numerador.1"
  store i32 %".22", i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

define i32 @"main"()
{
entry:
  %"retval" = alloca i32
  %".2" = getelementptr inbounds [3 x i8], [3 x i8]* @"fmt_scan_int_0", i32 0, i32 0
  %".3" = call i32 (i8*, ...) @"scanf"(i8* %".2", i32* @"ano")
  %".4" = load i32, i32* @"ano"
  %".5" = call i32 @"modulo"(i32 %".4", i32 400)
  %".6" = icmp eq i32 %".5", 0
  %".7" = load i32, i32* @"ano"
  %".8" = call i32 @"modulo"(i32 %".7", i32 4)
  %".9" = icmp eq i32 %".8", 0
  %".10" = or i1 %".6", %".9"
  %".11" = load i32, i32* @"ano"
  %".12" = call i32 @"modulo"(i32 %".11", i32 100)
  %".13" = icmp eq i32 %".12", 0
  %".14" = xor i1 %".13", -1
  %".15" = and i1 %".10", %".14"
  br i1 %".15", label %"if.then", label %"if.end"
if.then:
  %".17" = load i32, i32* @"ano"
  %".18" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_1", i32 0, i32 0
  %".19" = call i32 (i8*, ...) @"printf"(i8* %".18", i32 %".17")
  %".20" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_int_2", i32 0, i32 0
  %".21" = call i32 (i8*, ...) @"printf"(i8* %".20", i32 1)
  br label %"if.end"
if.end:
  store i32 0, i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

@"fmt_scan_int_0" = internal constant [3 x i8] c"%d\00"
@"fmt_print_int_1" = internal constant [4 x i8] c"%d\0a\00"
@"fmt_print_int_2" = internal constant [4 x i8] c"%d\0a\00"