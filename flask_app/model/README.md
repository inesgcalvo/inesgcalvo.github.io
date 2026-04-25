# Model Files

Place the two trained model files from `neuro_papers_db/model/` here:

| File | Source |
|------|--------|
| `qda_model.pkl` | `neuro_papers_db/model/qda_model.pkl` |
| `label_encoder.pkl` | `neuro_papers_db/model/label_encoder.pkl` |

You can download them directly from GitHub:

```bash
# From the flask_app/model/ directory:
curl -L -o qda_model.pkl \
  "https://github.com/inesgcalvo/neuro_papers_db/raw/main/model/qda_model.pkl"

curl -L -o label_encoder.pkl \
  "https://github.com/inesgcalvo/neuro_papers_db/raw/main/model/label_encoder.pkl"
```

> **Note**: These `.pkl` files are tracked by Git LFS in the source repo.  
> If the direct download doesn't work, copy them manually from your local clone of `neuro_papers_db`.

Once both files are present, the Flask app will automatically load them at startup.
