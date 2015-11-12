# -*- coding: utf-8 -*-
""" @package example.doxygen_example
用Doxygen文档化的范例

@brief Doxygen Python示例

@author Victor <gaoliqi@weizoom.com>
@version $Id$


Doxygen支持Markdown。详细文档参考：[Markdown support](http://www.stack.nl/~dimitri/doxygen/manual/markdown.html)

目录

[TOC]

\tableofcontents


> 用 \\tableofcontents 也可以

段落
=========
Markdown中不按换行区分段落，用空行分隔段落。例如：

    这是第一个段落。

    这是第二个段落。


表格
=========

表格示例
-----------

表格示例1：

| 参数  | 必需 | 说明 |
| :----------- | :---: | :-------------------------------------------- |
| articles      | 是     | 图文消息，一个图文消息支持1到10条图文    |
| thumb_media_id | 是 | 图文消息缩略图的media_id，可以在基础支持-上传多媒体文件接口中获得 |
| author | 否 | 图文消息的作者 |
| title | 是 | 图文消息的标题 |
| content_source_url | 否 | 在图文消息页面点击“阅读原文”后的页面 |
| content | 是 | 图文消息页面的内容，支持HTML标签 |
| digest | 否    | 图文消息的描述 |

表格示例2：

First Header  | Second Header
------------- | -------------
Content Cell  | Content Cell 
Content Cell  | Content Cell 


Doxygen指令
-----------


Doxygen指令 |  说明
-------------- | -------------------
\@param      | 参数说明
\@type         | 参数类型
\@see           | 参考
\@brief         | 简要说明，在doxygen生成的目录中显示
\@note         | 值得注意的问题
\@author      | 作者
\@attention  | 注意事项
\@bug          | bug
\@warning   | 警告

@see  更多指令参见 http://www.stack.nl/~dimitri/doxygen/manual/commands.html

引用块
==========

> This is a block quote
> spanning multiple lines

列表
==========

无编号列表：

- Item 1

  More text for this item.

- Item 2
  + nested list item.
  + another nested item.
- Item 3


有编号列表：

1. Item1 of list 1
3. Item2 of list 1
2. Item1 of list 2
4. Item2 of list 2


-# item1
-# item2

用*的列表：
* item 1
* item 2



代码块(Fenced Code Blocks)
============


Python代码示例
-----------------

有标号的代码块：

~~~~~~~~~~~~~~~~~~~~~~{.py}
    # A class
    if __name__=="__main__":
        print("Hello, world!")
~~~~~~~~~~~~~~~~~~~~~~


~~~~~~~~~~~~~~~~~~~~~
    # A class
    class Dummy:
        pass
~~~~~~~~~~~~~~~~~~~~~

C代码示例
---------------

~~~~~~~~~~~~~~~{.c}
int func(int a,int b) {
     return a*b;
}
~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~
    int func(int a,int b) {
         return a*b;
    }
~~~~~~~~~~~~~~~

水平线
==========

- - -
______


强调(Emphasis)
==========

*single asterisks*

_single underscores_

**double asterisks**

__double underscores__


Code spans
==========

Use the `println()` function.


链接
==========

* <http://www.example.com>
* <https://www.example.com>
* <ftp://www.example.com>
* <mailto:address@example.com>
* <address@example.com>
* [http://www.weizoom.com]
* [The link text](http://example.net/)
* [The link text](http://example.net/ "Link title")
* [The link text](/relative/path/to/index.html "Link title") 
* [The link text](somefile.html) 

I get 10 times more traffic from [Google] than from [Yahoo] or [MSN].

[google]: http://google.com/        "Google"
[yahoo]:  http://search.yahoo.com/  "Yahoo Search"
[msn]:    http://search.msn.com/    "MSN Search"

参考资料
==========
@see http://www.stack.nl/~dimitri/doxygen/manual/index.html


"""



def myfunction(arg1, arg2, kwarg='whatever.'):
    """
    Does nothing more than demonstrate syntax.

    This is an example of how a Pythonic human-readable docstring can
    get parsed by doxypypy and marked up with Doxygen commands as a
    regular input filter to Doxygen.

    @param[in] arg1 A positional argument.
    @param[in] arg2 Another positional argument.
    @param[out] kwarg  A keyword argument.

    @return 返回结果说明。A string holding the result.

    @retval 返回值

    @param arg1 A positional argument.
    @param arg2 Another positional argument.
    @param kwarg  A keyword argument.

    @note \@note 值得注意的问题
    
    @attention 注意事项

    @see http://wiki.weizoom.com:81/

    @warning \@warning 警告

    Raises:
        ZeroDivisionError, AssertionError, & ValueError.

    Examples:

        >>> myfunction(2, 3)
        '5 - 0, whatever.'
        >>> myfunction(5, 0, 'oops.')
        Traceback (most recent call last):
            ...
        ZeroDivisionError: integer division or modulo by zero
        >>> myfunction(4, 1, 'got it.')
        '5 - 4, got it.'
        >>> myfunction(23.5, 23, 'oh well.')
        Traceback (most recent call last):
            ...
        AssertionError
        >>> myfunction(5, 50, 'too big.')
        Traceback (most recent call last):
            ...
        ValueError

    @todo 待做列表
    
    改进1
     * 改进2

    @bug \@bug 存在的bug

    bug的描述....

    """
    assert isinstance(arg1, int)
    """
    @bug \@bug 存在的bugs
    bug的描述....
    """
    if arg2 > 23:
        raise ValueError

    """
    @todo 待做列表1
    """
    return '{0} - {1}, {2}'.format(arg1 + arg2, arg1 / arg2, kwarg)