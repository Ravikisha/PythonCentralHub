---
title: Example Guide
description: A guide in my new Starlight docs site.
---

Guides lead a user through a specific task they want to accomplish, often with a sequence of steps.
Writing a good guide requires thinking about what your users are trying to do.

## Further reading

- Read [about how-to guides](https://diataxis.fr/how-to-guides/) in the Diátaxis framework

```python title="main.py" showLineNumbers{1}
from starlette.applications import Starlette
from starlette.responses import JSONResponse

app = Starlette(debug=True)
app.add_route("/", homepage)
app.add_route("/items/{item_id}", item_detail) ==> lkjsddddddddddddddddddddddddddddddddddddddddddddddahjdfhlaksjdfahlsjdjfhlaskdjfhlskjdh
```

```js title="somethingComponent.ts" {1,3,5-6} showLineNumbers{1}
import SyntaxHighlighter from "react-syntax-highlighter";
import { docco } from "react-syntax-highlighter/dist/esm/styles/hljs";
const CodeBlock = ({ codestring }) => {
  return (
    <SyntaxHighlighter language="javascript" style={docco}>
            {codeString}
    </SyntaxHighlighter>
  );
};
```

```js title="react.jsx" showLineNumbers{1} 
const [age, setAge] = useState(50);
const [name, setName] = useState('Taylor');
```