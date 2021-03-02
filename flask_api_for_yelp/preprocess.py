def get_summary(raw_text, category=''):

    # !pip install spacy
    # !pip install spacytextblob
    # !pip install lemminflect
    # !pip install spacy_langdetect
    # !pip install spacymoji
    # !python -m spacy download en_core_web_md
    # !pip install more_itertools
    # !pip install html2text
    # nltk.download('stopwords')

    # !pip install bert-extractive-summarizer
    # !pip install torch


    from html2text import html2text
    import spacy
    from spacytextblob.spacytextblob import SpacyTextBlob
    import lemminflect
    from collections import Counter, defaultdict
    from spacy_langdetect import LanguageDetector
    from spacymoji import Emoji
    import pandas as pd
    import numpy as np
    import nltk
    from nltk.corpus import stopwords
    from afinn import Afinn
    import re
    import json


    nlp = spacy.load('en_core_web_md')
    nlp.add_pipe(Emoji(nlp, merge_spans=False), first=True)
    nlp.add_pipe(SpacyTextBlob())
    nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)


    # file = 'raw_text.txt'
    # with open(file) as f:
    #     raw_text = html2text(f.read())
    raw_text = html2text(raw_text)

    category = 'Pizza, Italian, Indian'
    category_list = re.sub('[^a-zA-Z ]','', category.lower()).split()
    category_set = set(category_list)
    category = nlp(' '.join(category_list))



    afinn = Afinn()

    doc = nlp(raw_text)
    seen_noun_chunks = set()
    noun_chunk_freq = Counter()
    noun_chunk_relevance = Counter()
    sent_associated_with_hash = {}
    hashes_associated_with_topic = defaultdict(set)
    nlp_cache = {}


    sentencesDF = pd.DataFrame(columns = ['SentenceID', 'SentenceText', 'SentenceTopics', 'SentenceSentiment']) 
    topicsDF = pd.DataFrame(columns = ['Topic', 'Frequency', 'SentenceHashes', 'Subjectivity', 'Polarity',  'Relevance']) 
    stop_words = set(stopwords.words('english'))  

    for sent in doc.sents:
      # ignore nonenglish sentences
      if sent._.language['language'] != 'en': continue

      # remove sentences with I as subject
      # if any(token.dep_ == 'nsubj' and token.tag_ == 'PRP' and token.text == 'I' for token in sent): continue
      if any(token.dep_ == 'nsubj' and token.text.lower() in ['i', 'we'] \
             or token.tag_ in ['dative', 'pobj', 'attr'] or token.text.lower() in ['me', 'us', 'mine', 'myself', 'my'] \
             for token in sent):
        continue

      # replace emojis with emoji descriptions
      if sent._.has_emoji:
        phrases = []
        for token in sent:
          if token._.is_emoji:
            if token._.emoji_desc:
              phrases.append(token._.emoji_desc)
          else:
            phrases.append(token.text)
        sent_text = ' '.join(phrases)
      else:
        sent_text = sent.text

      # sent_text = remove_tags(sent_text) # no need since rawtext already is converted from html to text
      sent_text = sent_text.replace(',', '')
      sent_associated_with_hash[hash(sent_text)] = sent_text
      topics = []
      scores = afinn.score(str(sent_text))


      
      for noun_chunk in sent.noun_chunks:
        # remove noun chunks that have no vector or contain pronoun
        if any(noun.is_oov or noun.tag_ == 'PRP' for noun in noun_chunk): continue      
        
        # remove heavily polarized topics, ie. amazing meal, good food
        if not (-0.33 <= noun_chunk._.sentiment.polarity <= 0.33): continue
        
        noun_chunk_text_arr = noun_chunk.text.split()

        remove = []
        for w in noun_chunk_text_arr:
          if w in stop_words:
            remove.append(w)
        for x in remove:
          while x in noun_chunk_text_arr:
            noun_chunk_text_arr.remove(x)


        if len(noun_chunk_text_arr) == 0:
          continue
      
        # remove articles
        if noun_chunk[0].pos_ == 'DET':
          noun_chunk_text_arr[0] = ''
        
        # make singular
        noun_chunk_text_arr[-1] = noun_chunk[-1]._.inflect('NN')

        noun_chunk_text = ' '.join(noun_chunk_text_arr).lstrip()

        # make noun chunk lowercase
        noun_chunk_text = noun_chunk_text.lower()

        if len(set(noun_chunk_text.split()) & category_set) >= 1:
        # if 'pizza' in noun_chunk_text or 'italian' in noun_chunk_text or 'indian' in noun_chunk_text:
            continue
        
        # for noun chunk text topic add the sentence hash
        hashes_associated_with_topic[noun_chunk_text].add(hash(sent_text))
        topics.append(noun_chunk_text)


        # remove noun chunks that have been seen before
        if hash(noun_chunk_text) in seen_noun_chunks:
          noun_chunk_freq[noun_chunk_text] += 1
          topicsDF.loc[(topicsDF['Topic'] == noun_chunk_text), 'SentenceHashes'] = np.array(hashes_associated_with_topic[noun_chunk_text])
          topicsDF.loc[(topicsDF['Topic'] == noun_chunk_text),'Frequency'] =  noun_chunk_freq[noun_chunk_text]
          continue

        seen_noun_chunks.add(hash(noun_chunk_text))
        noun_chunk_freq[noun_chunk_text] += 1
        nlp_cache[noun_chunk_text] = noun_chunk

        topicsDF = topicsDF.append({'Topic':noun_chunk_text, 'Frequency': noun_chunk_freq[noun_chunk_text], 'SentenceHashes':  np.array(hashes_associated_with_topic[noun_chunk_text]) , 'Subjectivity': noun_chunk._.sentiment.subjectivity , 'Polarity': noun_chunk._.sentiment.polarity, 'Relevance': noun_chunk.similarity(category) }, ignore_index=True)
        
      
                       
        # print noun chunk relevance to main topic
        noun_chunk_relevance[noun_chunk_text] = noun_chunk.similarity(category)
        # print(noun_chunk.similarity(category), noun_chunk_text)
      sentencesDF = sentencesDF.append({'SentenceID': hash(sent_text), 'SentenceText' : sent_text, 'SentenceTopics': topics, 'SentenceSentiment' :   scores}, ignore_index = True)
      


    for idx,row in topicsDF.iterrows():
      topicsDF.at[idx, 'relevanceXfrequency'] = row.Frequency * row.Relevance






    # find out number of topics in table
    num_rows, num_cols = topicsDF.shape

    # define number of topics we want
    ideal_num_topics = min(max(5, int(num_rows**(5/12))), 25) # a minimum 5, at most 25, in between use lenght^(5/12)

    # combine topics from most frequent and most relevant
    neutral_topics = topicsDF[(topicsDF['Subjectivity'] < 0.5) & (topicsDF['Frequency'] > 2)]
    highest_frequency_topics = set(neutral_topics.sort_values('Frequency', ascending=False)['Topic'].head(ideal_num_topics).tolist())
    highest_relevance_topics = set(neutral_topics.sort_values('Relevance', ascending=False)['Topic'].head(ideal_num_topics).tolist())
    chosen_topics = highest_frequency_topics.union(highest_relevance_topics)


    # print result
    print(*chosen_topics, sep='\n', end='\n\n\n')


    TPURPLE =  '\033[35m'
    TBLACK =  '\033[30m'


    # Comment out for quick summary
    # from summarizer import Summarizer
    # model = Summarizer()


    summary_by_topic = {}

    for chosen_topic in chosen_topics:
        print(TPURPLE + chosen_topic + TBLACK)
        sent_hashes = topicsDF.loc[topicsDF['Topic'] == chosen_topic, 'SentenceHashes'].item()

        if isinstance(sent_hashes,(np.ndarray)):
            sent_hashes = sent_hashes.tolist()


        # Quick Summary
        result = ' '.join([sentencesDF.loc[sentencesDF['SentenceID'] == target_hash, 'SentenceText'].values[0].rstrip('\n') for target_hash in list(sent_hashes)[:3]])
        result = result.replace('\n', ' ')
        print(result)


        # Bert Summary
        # if len(sent_hashes) > 3:
        #     body = ' '.join([sentencesDF.loc[sentencesDF['SentenceID'] == target_hash, 'SentenceText'].values[0].rstrip('\n') for target_hash in sent_hashes]).replace('\n', ' ')
        #     result = model(body, num_sentences=3)  # Will return 3 sentences
        #     print(result)
        # else:
        #     result = ' '.join([sentencesDF.loc[sentencesDF['SentenceID'] == target_hash, 'SentenceText'].values[0].rstrip('\n') for target_hash in sent_hashes])
        #     print(result)
        
        print('\n')

        summary_by_topic[chosen_topic] = result

    # return json.dumps(summary_by_topic)
    return summary_by_topic










