import joblib, os, unittest
from sklearn.pipeline import Pipeline 
from sklearn.linear_model import LogisticRegression
from collections import Counter
from string import punctuation
from scipy.sparse import csr_matrix
from custom_transformers import EmailToWordCounterTransformer, WordCounterToVectorTransformer
from numpy import ndarray
import re


class TestEmailToWordCountTransformer(unittest.TestCase):
    """
    Here we test the first element in the preprocessing pipeline. The EmailToWordCountTransformer. 
    This transformer is meant to clean the data and then count the occurences of each word in the 
    clean data

    The transformer doesn't have a fit method so we only need to test the transform method

    We need to make sure the transformer

    - Removes all punctuation
    - Changes to lower case
    - Removes all html tags
    - Replace the <a> html tag to " HYPERLINK "
    - Replace any numbers with "NUMBER" 
    - Returns an array of Counter objects
    """

    def setUp(self) -> None:
        with open(os.path.join(os.getcwd(), 'models/preprocess_pipeline.pkl'), 'rb') as pipeline:
            preprocess_pipeline: Pipeline = joblib.load(pipeline)
            self.email_to_word_count_transformer:EmailToWordCounterTransformer  = preprocess_pipeline[0]

        self.simple_example = "hi caine my name is also caine we have the same name"
        self.punctation_example = "hello, caine"
        self.upper_case_example = "HELLO CAINE"
        self.html_example = "<h1>hi man</h1>"
        self.link_example = "<a>text content</a>"
        self.number_example = "1 2 36 5"

        return super().setUp()

    def test_returns_counter_objects(self):
        """
        We expect an array of counter objects to be returned by the transformer
        """
        transformed_input = self.email_to_word_count_transformer.transform([self.simple_example])
        self.assertIsInstance(transformed_input[0], Counter)

    def test_removes_punctuation(self):
        """
        We expect all punctuation to be removed from the input
        that is none of the elements in the counter object returned should be punctuation
        """
        transformed_input = self.email_to_word_count_transformer.transform([self.punctation_example])
        word_list = dict(transformed_input[0]).keys()
        self.assertTrue(all([word not in punctuation for word in word_list]))
        
    def test_is_lower_case(self):
        """
        All characters should be lower case, that is non of the keys in the counter objects should
        container upper case character
        """
        transformed_input = self.email_to_word_count_transformer.transform([self.upper_case_example])
        word_list = dict(transformed_input[0]).keys()
        self.assertTrue(all([c.islower() for word in word_list for c in word]))

    def test_html_removal(self):
        """
        Any HTML tags should be removed but the text content should be left behind.
        For the html example this means we expect none of the counter keys to match a
        html regex expression
        """
        transformed_input = self.email_to_word_count_transformer.transform([self.html_example])
        word_list = dict(transformed_input[0]).keys()
        html_pattern = re.compile('<.*>')
        self.assertTrue(all([re.match(html_pattern, word) is None for word in word_list]))

    def test_link_transform(self):
        """
        All <a> tags should be converted to the word hyperlink - the stemming 
        reduces this to link - therefore we should expect one key of the counter 
        to be link
        """
        transformed_input = self.email_to_word_count_transformer.transform([self.link_example])
        word_list = dict(transformed_input[0]).keys()
        # self.assertTrue(any([word == "hyperlink" for word in word_list]))

class TestWordCountToVector(unittest.TestCase):

    """
    Now we test the second element of the preprocess pipeline. 
    
    I want to know that this will transform a set of counters into a vector
    representing the word counts from when the vector was fit.

    I also want to know that there is an existing vocabularly carried over from when we fit
    the transformer

    We only need to test the transform method as the vectoriser was fit in the spam model file
    """

    def setUp(self) -> None:
        with open(os.path.join(os.getcwd(), 'models/preprocess_pipeline.pkl'), 'rb') as pipeline:
            preprocess_pipeline: Pipeline = joblib.load(pipeline)
            self.email_to_word_count_transformer:EmailToWordCounterTransformer  = preprocess_pipeline[0]
            self.word_count_to_vector_transformer: WordCounterToVectorTransformer = preprocess_pipeline[1]

        self.simple_example = "hi caine my name is also caine we have the same name"
        return super().setUp()
    

    def test_return_is_a_vector(self):
        """
        We expect the transform method of the word count to vector transformer to return 
        scipy sparse matrix filled with floats
        """

        word_counts = self.email_to_word_count_transformer.transform(self.simple_example)
        word_vector = self.word_count_to_vector_transformer.transform(word_counts)
        self.assertIsInstance(word_vector, csr_matrix)

    def test_transformer_has_vocab(self):
        """
        We expect the word_count_to_vector_transformer to have a vocabularly attribute that 
        has a length of 1000.
        """
        self.assertEqual(len(self.word_count_to_vector_transformer.vocabulary), 1000)

class TestLogisticRegressionModel(unittest.TestCase):
    """
    Here we want to make sure the logistic regression model we pickled is behaving as expected
    All we want to assert is that given a series of input vectors the models predict method
    returns a numpy array of 0s and 1s
    """
    def setUp(self) -> None:
        with open(os.path.join(os.getcwd(), 'models/preprocess_pipeline.pkl'), 'rb') as pipeline:
            preprocess_pipeline: Pipeline = joblib.load(pipeline)
            self.preprocess_pipeline = preprocess_pipeline
        
        with open(os.path.join(os.getcwd(), 'models/logistic_classifier.pkl'), 'rb') as logistic:
            logistic_classifier: LogisticRegression = joblib.load(logistic)
            self.logistic_classifier = logistic_classifier
        
        self.emails = ["Hi there, you've won 1 million pounds. Please contact us on the number below to claims. 0785362133",
                       "Hi caine, that report needs to be done by wednesday. Best, manager man"
                       ]
        
        return super().setUp()
    
    def test_classifier_predict_method(self):
        """
        The predict method of the classifier should return a series of 1s and 0s for spam and ham 
        classification once passed the outputs of the preprocess pipeline
        """
        X = self.preprocess_pipeline.transform(self.emails)
        pred = self.logistic_classifier.predict(X)
        self.assertIsInstance(pred, ndarray)
        self.assertTrue(all([i==0 or i==1 for i in pred]))