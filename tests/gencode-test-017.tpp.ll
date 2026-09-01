; ModuleID = "gencode-test-017.tpp"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

@"A" = common global [10 x double] zeroinitializer, align 4
@"B" = common global [10 x double] zeroinitializer, align 4
@"C" = common global [10 x double] zeroinitializer, align 4
define void @"somaVetores"(i32 %"n")
{
entry:
  %"n.1" = alloca i32
  store i32 %"n", i32* %"n.1"
  %"i" = alloca i32
  store i32 0, i32* %"i"
  br label %"repeat.body"
repeat.body:
  %".6" = load i32, i32* %"i"
  %".7" = getelementptr [10 x double], [10 x double]* @"C", i32 0, i32 %".6"
  %".8" = load i32, i32* %"i"
  %".9" = getelementptr [10 x double], [10 x double]* @"A", i32 0, i32 %".8"
  %".10" = load double, double* %".9"
  %".11" = load i32, i32* %"i"
  %".12" = getelementptr [10 x double], [10 x double]* @"B", i32 0, i32 %".11"
  %".13" = load double, double* %".12"
  %".14" = fadd double %".10", %".13"
  store double %".14", double* %".7"
  %".16" = load i32, i32* %"i"
  %".17" = add i32 %".16", 1
  store i32 %".17", i32* %"i"
  %".19" = load i32, i32* %"i"
  %".20" = load i32, i32* %"n.1"
  %".21" = icmp eq i32 %".19", %".20"
  br i1 %".21", label %"repeat.end", label %"repeat.body"
repeat.end:
  br label %"exit"
exit:
  ret void
}

define i32 @"main"()
{
entry:
  %"retval" = alloca i32
  %"i" = alloca i32
  store i32 0, i32* %"i"
  br label %"repeat.body"
repeat.body:
  %".4" = load i32, i32* %"i"
  %".5" = getelementptr [10 x double], [10 x double]* @"A", i32 0, i32 %".4"
  %".6" = sitofp i32 1 to double
  store double %".6", double* %".5"
  %".8" = load i32, i32* %"i"
  %".9" = getelementptr [10 x double], [10 x double]* @"B", i32 0, i32 %".8"
  %".10" = sitofp i32 1 to double
  store double %".10", double* %".9"
  %".12" = load i32, i32* %"i"
  %".13" = add i32 %".12", 1
  store i32 %".13", i32* %"i"
  %".15" = load i32, i32* %"i"
  %".16" = icmp eq i32 %".15", 10
  br i1 %".16", label %"repeat.end", label %"repeat.body"
repeat.end:
  call void @"somaVetores"(i32 10)
  store i32 0, i32* %"i"
  br label %"repeat.body.1"
repeat.body.1:
  %".21" = load i32, i32* %"i"
  %".22" = getelementptr [10 x double], [10 x double]* @"C", i32 0, i32 %".21"
  %".23" = load double, double* %".22"
  %".24" = getelementptr inbounds [4 x i8], [4 x i8]* @"fmt_print_float_0", i32 0, i32 0
  %".25" = call i32 (i8*, ...) @"printf"(i8* %".24", double %".23")
  %".26" = load i32, i32* %"i"
  %".27" = add i32 %".26", 1
  store i32 %".27", i32* %"i"
  %".29" = load i32, i32* %"i"
  %".30" = icmp eq i32 %".29", 10
  br i1 %".30", label %"repeat.end.1", label %"repeat.body.1"
repeat.end.1:
  store i32 0, i32* %"retval"
  br label %"exit"
exit:
  %"ret.final" = load i32, i32* %"retval"
  ret i32 %"ret.final"
}

@"fmt_print_float_0" = internal constant [4 x i8] c"%f\0a\00"