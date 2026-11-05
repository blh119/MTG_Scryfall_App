# MTG Card Recommendation Engine

A content-based recommendation engine for *Magic: The Gathering*. Give it the name of a card and it returns the five most similar cards, based on each card's colors, types, abilities, and rules text.

The app pulls card data from the [Scryfall API](https://scryfall.com/docs/api), turns every card into a feature vector, and ranks other cards by cosine similarity. A companion notebook groups cards with k-means clustering and explores what defines each cluster.

## How it works

1. **Data collection.** Downloads Scryfall's bulk card data plus its official lists of card types, subtypes, keyword abilities, keyword actions, and ability words.
2. **Cleaning.** Removes tokens and basic lands, keeps first printings, splits double-faced cards, and cleans power, toughness, and loyalty values.
3. **Feature engineering.**
   - One-hot encodes colors (for example, an Azorius card gets a 1 for white and a 1 for blue), supertypes, card types, subtypes, keywords, and rarity
   - Counts colored mana pips in the mana cost
   - Tokenizes card names, rules text, and type lines with NLTK, trains a [fastText](https://radimrehurek.com/gensim/models/fasttext.html) model with gensim, and builds TF-IDF-weighted average word vectors for each card
4. **Recommendation.** Scales the features, then uses cosine similarity to find the five cards closest to the input card.

## Clustering analysis

`Card Recommeder Notebook.ipynb` runs k-means clustering on PCA-reduced card features to see which kinds of cards group together. The clusters are visualized with t-SNE and explained with random forest feature importance.

| | |
| --- | --- |
| ![t-SNE view of the k-means clusters](graphs/tsne%20cluster.png) | ![Random forest feature importance](graphs/random%20forest%20feature%20importance.png) |
| ![Color by cluster](graphs/color%20by%20cluster.png) | ![Card type by cluster](graphs/card%20type%20by%20cluster.png) |

## Running the app

Requires Python 3 and the following packages:

```
pip install requests pandas numpy nltk gensim scikit-learn matplotlib
```

Then run:

```
python main.py
```

The first run downloads the Scryfall data and trains the text models, so it can take a few minutes. After that, the app asks whether you want a recommendation and which card to look up:

```
Which card would you like a recommendation for?
> Grave Pact
```

It prints the input card's type, mana cost, and rules text, followed by the five recommended cards. You can keep asking for recommendations or enter `N` to quit.

## Project files

| File | Purpose |
| --- | --- |
| `main.py` | Entry point: loads data, trains the models, and starts the command-line app |
| `utils.py` | Data processing (`MTGDataProcessor`), the recommender (`CardRecommenderModel`), visualizations (`DataVisuals`), and the command-line interface |
| `constants.py` | Scryfall URLs, selected columns, stopwords, and other settings |
| `Card Recommeder Notebook.ipynb` | Exploration and the k-means clustering analysis |
| `graphs/` | Saved cluster and feature-importance charts |

## Built with

Python, pandas, NumPy, NLTK, gensim (fastText), scikit-learn (TF-IDF, PCA, k-means, random forest, t-SNE, cosine similarity), Matplotlib, and the Scryfall API.

Card data is provided by Scryfall. This project is not affiliated with Wizards of the Coast.
