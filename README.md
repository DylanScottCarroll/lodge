# Lodge
The implementation of the compiler for the Lodge programming language.

See the [lodge specification repository](https://github.com/DylanScottCarroll/lodge_spec) for a description of the Lodge Programming language.


# Project Stages

## 1. Python-based Interpreter
This is the current stage of the project.

This stage is a neccesary bootstrapping stage as the final stage of the project will be written in Lodge itself. Python was chosen as an intermediate because of how quickly it can be worked with. 

The intent is to create an implementation of the most minimal subset of the Lodge programming language that can be used to write a more sophisticated interpreter and compiler. The python interperer will be discarded once a compiler exists.

## 2. Lodge-based Interpreter

This is the second part of the bootstrapping process. The intent of this stage is to transliterate the python interpreter and then extend it to a mostly complete implementation of the specification. 

This stage is impprtant as it is the first stage that will be kept. The intention is that the final version of Lodge will be able to be interpreted or compiled. It will also be the fondation for building the compiler. 

## 3. Lodge Compiler
This is the final goal of the project. The intent is to be able to compile Lodge to native binaries.

Once a functional Lodge-based interpreter exists, it will be extended with an LLVM backend that can compile Lodge into native binaries. Once that is possible, the compiler can compile itself, transcending the need for the python interpreter.

## 4. Fully-Featured Lodge

Once a pure-Lodge backend exists, efforts will be focused on implementing all of the language features and creating a stable and usable version of Lodge.



# Project Status

## September 28th 2024
Recently, the Lodge specification has reached a point where the syntax has stabilized for the most part, allowing work to begin on a concrete implementation. As of today, a parser capable of consuming arbitrary LR(1) context-free grammars has been created. The next step is to begin converting the specification into a complete context-free grammar describing Lodge's syntax that can run in the parser.

