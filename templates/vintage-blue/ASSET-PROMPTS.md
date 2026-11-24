# Vintage Blue: replacing the illustrations

The files in `assets/` are drawn by code (`tools/draw.py`, rasterised by `tools/render.mjs`). To make them look painted, generate replacements (with ChatGPT image generation, for example) and save them over the files under the **same name, same aspect ratio, as WebP**. The layout depends on the aspect ratios. Files marked *transparent* need a transparent background. Export PNG and convert:

```sh
python3 -c "from PIL import Image; Image.open('in.png').save('out.webp', quality=80)"
```

Shared style for every prompt: *vintage French toile de Jouy engraving, powder blue and soft periwinkle ink on off-white paper, with warm gold accents, delicate copper-plate hatching, elegant wedding stationery, no text, no people.*

| File | Size (px) | Transparent | Prompt |
|---|---|---|---|
| `sky.webp` | 960×1800 | no | Pale misty sky, soft grey-blue clouds, faint paper grain, very light, no land. |
| `mountains-far.webp` | 960×920 | yes, above the ridge | Distant mountain range in pale blue toile engraving. The ridge sits about 40% from the top. Fade to white mist at the bottom. |
| `mountains-near.webp` | 960×920 | yes, above the ridge | Nearer hills in blue toile engraving, with a small walled hilltop palace on the right. The ridge sits about 50% from the top. Fade to mist at the bottom. |
| `forest.webp` | 960×1000 | yes, top 30% | Dense blue toile forest: round-canopy trees, cypresses and two small white cottages. The top fades out and the bottom is fully opaque. |
| `palm.webp` | 520×1120 | yes | Two gold-leaf palm trees, one tall and one shorter, engraved gold line art with trunks rooted at the bottom edge. |
| `flowers.webp` | 960×680 | yes, top half | A horizontal border of cream and pale-gold peonies, blue cabbage roses, gold acanthus leaves and small blue delphinium sprigs, densest along the bottom edge. |
| `castle.webp` | 640×480 | yes | A fairytale castle in blue watercolour with conical spires, resting on soft white clouds. |
| `frame.webp` | 600×800 | yes, including the oval centre | An ornate gold baroque oval mirror frame, empty and transparent inside. The inner oval spans about 73%×80%, centred. |
| `bouquet.webp` | 360×380 | yes | A small cluster: one cream peony, one blue rose and gold leaves, for the lower corner of the oval frame. |
| `leaves.webp` | 440×680 | yes | A spray of long gold and blue acanthus leaves fanning up from the bottom-left. |

Couple photos belong to each event (`events/<slug>/assets/`), not the template.
