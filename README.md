# Hu-Tucker-Algorithm
Алгоритм Ху-Таккера для курса "Теория кодирования"
## Постановка задачи
Введём основные понятия:

Пусть имеется ***алфавит*** ![img1](/img/A.png).

***Алфавитным деревом*** назовём дерево, в котором при просмотре листьев слева направо символы идут **в алфавитном порядке**, и **код последующего лексикографически больше предыдущего**.

***Алгоритм Ху-Таккера*** решает задачу построения оптимального алфавитного дерева и последующего выбора бинарных кодов.

## Описание алгоритма

### Определение
***Алгоритмом Ху-Таккера*** называют такой алгоритм выбора бинарных кодов ![img2](/img/C.png) для алфавита ![img](/img/A.png) с соответствующем ему набору весов символов ![img3](/img/W.png), что выполнены следующие условия:

- ![img4](/img/a_i.png) не является префиксом для ![img5](/img/a_j.png), при i≠j.
- для всех ![img8](/img/a_a.png) выполнено ![img6](/img/c_c.png)
- при удовлетворенности предыдущего условия, ![img7](/img/sum.png) минимальна.

### Описание алгоритма
#### Основные понятия
Две вершины называются ***совместимой парой***, если они соседние или если между ними нет вершин алфавита.

Две вершины называются ***минимальной парой***, когда их суммарный вес наименьший из всех. При равенстве весов выбирается пара с самой левой вершиной, из всех таких та, у которой правый узел расположен левее.

***Минимальной совместимой парой*** называется наименьшая пара из всех совместимых.

#### Ход алгоритма

Изначально имеется алфавит остсортированный лексикографически и соответствующие символам веса.

***Построение дерева (комбинирование):*** Представим алфавит как множество вершин. Из последовательности из n вершин будем создавать послебовательность из n-1 вершин, комбинируя минимальную совместимую пару и заменяя ее левую вершину вершиной с весом равном сумме весов пары и удаляя правую. Эта процедура повторяется до тех пор, пока не останется одна вершина. Таким образом, связывая вершины пары с вновь получившейся вершиной рёбрами, обеспечивается "рост" дерева от листьев к корню.

***Определение уровней:*** Проходом по дереву определяем уровень ![img9](/img/l_i.png) каждого листа относительно корня.

***Перестройка:*** Для перестройки дерева воспользуемся ***стековым алгоритмом перестройки***.

##### Стековый алгоритм перестройки
***Шаг 1:*** Если значение двух верхних элементов различно или в стеке всего один элемент перейти к ***шагу 2***, иначе к ***шагу 3***.

***Шаг 2:*** Поместить следующий элемент ![img10](/img/l_i.png) на вершину стека. Перейти к ***шагу 1***.

***Шаг 3:*** Удалить 2 верхних элемента стека, поместить в стек элемент со значением меньшим на единицу, чем удаленные. Если значение нового элемента равно нулю — остановиться, иначе перейти к ***шагу 1***.

В результате выполнения алгоритма мы получаем алфавитное дерево. Назначение кода каждому символу делается аналогично коду Хаффмана: левым ребрам назначается 0, а правым 1.

### Опиасние программы
#### Входные и выходные данные

***При сжатии***

- На ***вход*** программе подаётся файл с текстовой информацией.
- На ***выходе*** прогрмма формирует бинарный файл со сжатыми данными и метаинформацией.

***При получении исходного файла из сжатого***

- На ***вход*** программы подаётся бинарный файл со сжатыми данными и метаинформацией, сформированный ей же.
- На ***выходе*** программа формирует текстовый файл и исходными данными.
