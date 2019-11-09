# lib-daikaku-zh-cn
本库只采纳使用类似tex格式的形式编写的题目。同时也包含了tex生成的pdf文档。

为了利于排版，每一个文件都只包含了一个题目。同时使用一个小巧的python 程序来生成一份完整的tex试卷。

完整的tex试卷结构如下：
``` latex
\documentclass[a5paper]{ctexart}

\usepackage{amsmath}
\usepackage{enumitem}
\usepackage{tikz}

\setlist{leftmargin=4em, itemsep=0.1em, parsep=0em,
	itemindent=0em, listparindent=0em,
	labelwidth=1.5em, labelsep=1em}

\title{}

\begin{document}
	% ...
\end{document}
```

而每一个小题如下：(有点像markdown和latex的变种）
``` latex
$1+1=$
-------------------------------------------
- $2$
- $\lim_x\to 0 f(x)=x$
- 应该是四
- 以上答案都不对
```

使用python程序生成的tex文件应该如下：
``` latex
% ...
\begin{document}
	\begin{enumerte}
		\item {%
			$1+1=$
			\begin{enumerate}
				\item $2$
				\item $\lim_{x\to 0} f(x)=x$
				\item 应该是四
				\item 以上答案都不对
			\end{enumerate}
		}

		\item {%
			% ...
		}
	\end{enumerta}
\end{document}
```

所有题库都是基于自愿者上传，旨在减少学生的为了寻找题目而浪费的过多时间。

本项目不接受捐助。

如果你有好题目，不如
