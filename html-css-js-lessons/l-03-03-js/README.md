# Создание простого "калькулятора"

Привет! Сегодня мы научимся связывать HTML и JavaScript, чтобы страница реагировала на действия пользователя. Ты уже знаешь переменные и условия, а теперь добавим **функции** и атрибут **onclick** — с их помощью мы построим простой калькулятор.

## 1. Атрибут `onclick` – первый мостик между HTML и JS

Раньше наш код выполнялся сам по себе. Но как запустить JavaScript именно тогда, когда пользователь нажал кнопку? Для этого у HTML-элементов есть атрибут `**onclick**`. В него мы пишем вызов функции, который произойдёт при клике.

```html
<button onclick="alert('Привет!')">Нажми меня</button>
```

Когда пользователь нажмёт кнопку, сработает `alert` и появится всплывающее сообщение. Так мы передаём управление от HTML коду на JavaScript. Но писать всю логику прямо в атрибуте неудобно — лучше вызывать свою **функцию**.

## 2. Что такое функция и зачем она нужна

**Функция** — это именованный блок кода, который можно вызывать много раз. Она может принимать **параметры** (входные данные) и возвращать **результат** с помощью ключевого слова `return`.

Зачем нужны функции:
- **Избегать повторений** — написал один раз, используешь где угодно.
- **Структурировать программу** — разбить большую задачу на маленькие шаги.
- **Сделать код понятнее** — имя функции объясняет, что она делает.

Простой пример:

```js
function multiplyByTwo(number) {
  return number * 2;
}

let result = multiplyByTwo(5); // result будет 10
```

`return` не только возвращает значение, но и сразу завершает выполнение функции. Всё, что написано после `return`, никогда не выполнится.

## 3. Строим калькулятор – шаг за шагом

Теперь применим всё на практике. Наш калькулятор будет состоять из трёх рядов кнопок: для выбора первого числа, для знака операции и для второго числа, а также кнопки «=», которая выведет результат в консоль.

### 3.1. HTML-скелет калькулятора

Вот основа разметки. Обрати внимание: каждая кнопка содержит `onclick`, который вызывает определённую функцию с параметром.

```html
<h2>Калькулятор</h2>
<div class="status" id="status">Соберите выражение</div>

<!-- Первый ряд – выбор первого числа -->
<div class="row">
  <button onclick="selectFirst(1)">1</button>
  <button onclick="selectFirst(2)">2</button>
  <button onclick="selectFirst(3)">3</button>
  <!-- и так далее до 9 -->
</div>

<!-- Второй ряд – выбор знака операции -->
<div class="row">
  <button class="operator" onclick="selectOperator('+')">+</button>
  <button class="operator" onclick="selectOperator('-')">-</button>
  <button class="operator" onclick="selectOperator('*')">*</button>
  <button class="operator" onclick="selectOperator('/')">/</button>
</div>

<!-- Третий ряд – выбор второго числа -->
<div class="row">
  <button onclick="selectSecond(1)">1</button>
  <button onclick="selectSecond(2)">2</button>
  <!-- до 9 -->
</div>

<button class="equal-btn" onclick="calculateResult()">= (результат в консоль)</button>
```

Мы вызываем функции `selectFirst`, `selectOperator`, `selectSecond` и `calculateResult`. Сами функции мы опишем ниже, в блоке `<script>`.

### 3.2. Храним состояние калькулятора

Нам нужно помнить, какие числа и оператор выбрал пользователь. Для этого заведём переменные:

```js
let firstOperand = null;   // первое число
let operator = null;        // знак (+, -, *, /)
let secondOperand = null;   // второе число
const statusDiv = document.getElementById('status'); // для вывода подсказок
```

Когда пользователь нажимает кнопку, мы будем обновлять соответствующую переменную и показывать текущее выражение на странице.

### 3.3. Функция выбора первого числа

```js
function selectFirst(number) {
  firstOperand = number;
  console.log(\`Вы выбрали ${number}. Теперь ваше выражение: ${buildExpressionText()}\`);
  updateStatus(buildExpressionText());
}
```

Она записывает переданное число в переменную `firstOperand`, а затем обновляет сообщение.

### 3.4. Функция выбора оператора

```js
function selectOperator(op) {
  operator = op;
  console.log(\`Вы выбрали оператор "${op}". Теперь ваше выражение: ${buildExpressionText()}\`);
  updateStatus(buildExpressionText());
}
```

### 3.5. Функция выбора второго числа

```js
function selectSecond(number) {
  secondOperand = number;
  console.log(\`Вы выбрали ${number}. Теперь ваше выражение: ${buildExpressionText()}\`);
  updateStatus(buildExpressionText());
}
```

Все три функции используют вспомогательные инструменты, которые мы опишем дальше, чтобы не повторять код.

### 3.6. Вспомогательные функции `buildExpressionText` и `updateStatus`

Они делают код чище. Первая собирает строку вида "2 + ?", заменяя `null` на знак вопроса. Вторая обновляет текст на экране.

```js
function updateStatus(message) {
  statusDiv.textContent = message;
}

function buildExpressionText() {
  const first = firstOperand ?? '?';
  const op = operator ?? '?';
  const second = secondOperand ?? '?';
  if (firstOperand === null && operator === null && secondOperand === null) {
    return 'Соберите выражение';
  }
  return \`${first} ${op} ${second}\`;
}
```

Обрати внимание на оператор `??` — **оператор нулевого слияния**. Если значение слева равно `null` или `undefined`, он подставляет то, что справа. Здесь мы заменяем `null` на `'?'`, чтобы показать, что часть выражения ещё не выбрана.

### 3.7. Функция вычисления результата

Она вызывается при клике на «=». Сначала проверяем, всё ли выбрано. Затем, в зависимости от оператора, выполняем нужное действие. Для этого отлично подходит конструкция **switch** — она сравнивает значение с несколькими вариантами и выполняет подходящий код.

Синтаксис switch:
```js
switch (выражение) {
  case значение1:
    // код
    break;
  case значение2:
    // код
    break;
  default:
    // код, если ничего не совпало
}
```

Подробнее можно прочитать: **[switch](https://doka.guide/js/switch/)**.

А в ветке деления мы используем **тернарный оператор** — краткую форму `if/else` для присваивания. Он выглядит так:  
`условие ? значение_если_истина : значение_если_ложь`

Подробнее: **[тернарный оператор](https://doka.guide/js/ternary-operator/)**.

Вот сама функция:

```js
function calculateResult() {
  if (firstOperand === null || operator === null || secondOperand === null) {
    console.log('Выражение не завершено! Выберите оба числа и оператор.');
    return;
  }

  let result;
  switch (operator) {
    case '+': result = firstOperand + secondOperand; break;
    case '-': result = firstOperand - secondOperand; break;
    case '*': result = firstOperand * secondOperand; break;
    case '/':
      // Тернарный оператор защищает от деления на ноль
      result = secondOperand !== 0 ? firstOperand / secondOperand : 'Ошибка (деление на 0)';
      break;
    default: result = 'Неизвестная операция';
  }

  console.log(\`Результат: ${firstOperand} ${operator} ${secondOperand} = ${result}\`);
  updateStatus(\`${firstOperand} ${operator} ${secondOperand} = ${result}\`);
}
```

## 4. Что мы изучили

- **Атрибут `onclick`** – способ запускать JavaScript-код по клику на HTML-элементе.
- **Функции** – переиспользуемые блоки кода с параметрами и возвратом значения через `return`.
- **Практика связки HTML и JS** – построили работающий калькулятор, где нажатия кнопок меняют переменные и выводят сообщения.
- Познакомились с **`switch`** и **тернарным оператором** – альтернативными способами проверки условий.
- Научились использовать **оператор нулевого слияния `??`** для подстановки значений по умолчанию.

Теперь у тебя есть основа для интерактивных страниц. Дальше можно усложнять калькулятор: добавить десятичные числа, цепочки операций или переписать его с использованием `addEventListener` — это будет следующим шагом в изучении DOM.