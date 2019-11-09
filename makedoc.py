def ltmd2latex(s:str):
    """
    input will like:
    |   $1+1=$
    |   -------------------------
    |   - $2$
    |   - $\lim_{x\to 0} f(x)=x$
    |   - maybe 4
    |   - there is no corrent anwser
    and then output will be:
    |   $1+1=$
    |   \begin{enumerate}[A.]
    |       \item $2$
    |       \item $\lim_{x\to 0} f(x)=x$
    |       \item maybe 4
    |       \item there is no corrent anwser
    |   \end{enumerate}
    """
    
