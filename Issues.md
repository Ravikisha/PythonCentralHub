## Manifest Issue
#### #1
- [ ] **Issue:** The `manifest.json` file has missing 144x144 icon.
```json
{
      "src": "images/icons/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png"
},
```

#### #2 Some Code Reference
import FileCode from '../../../components/FileCode.astro'


<FileCode file="package.json" lang="json" title="Package" meta="{1}" />

```mermaid title="A flowchart" desc="This is a diagram"
flowchart TD
    A[Start] --> B{Is it?}
    B -->|Yes| C[OK]
    C --> D[Rethink]
    D --> B
    B ---->|No| E[End]
```