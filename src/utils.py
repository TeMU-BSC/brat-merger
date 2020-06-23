import difflib
import os
import string
import src.const as const


class Utils:

    fileDir = os.path.dirname(os.path.abspath(__file__))
    parentDir = os.path.dirname(fileDir)
    #
    # @staticmethod
    # def get_path():
    #     fileDir = os.path.dirname(os.path.abspath(__file__))
    #     parentDir = os.path.dirname(fileDir)
    #
    #     return parentDir

    @staticmethod
    def span_fixer(text, start_span, end_span, label):
        punctuation = string.punctuation
        before_rstrip = len(text)
        text = text.rstrip()
        after_rstrip = len(text)
        end_span -= before_rstrip - after_rstrip
        while text[len(text) - 1] in punctuation:
            text = text[:-1]
            removed_space = len(text) - len(text.rstrip())
            text = text.rstrip()
            end_span -= 1 + removed_space
        before_lstrip = len(text)
        text = text.lstrip()
        after_lstrip = len(text)
        start_span += before_lstrip - after_lstrip
        while text[0] in string.punctuation:
            text = text[1:]
            removed_space = len(text) - len(text.lstrip())
            text = text.lstrip()
            start_span += 1 + removed_space

        return text, start_span, end_span

    @staticmethod
    def similarity_hemorragia_evidence(text):
        """
        :param line: input line
        :return:
            The most similarity defined section with the given line
        """

        list_similarities = difflib.get_close_matches(text, const.HEMORRAGIA_EVIDENCE, 1, 0.85)
        if len(list_similarities) > 0:
            return True
        else:
            return False

    @staticmethod
    def similarity_isquemico_evidence(text):
        """
        :param line: input line
        :return:
            The most similarity defined section with the given line
        """

        list_similarities = difflib.get_close_matches(text, const.ISQUEMICO_EVIDENCE, 1, 0.85)
        if len(list_similarities) > 0:
            return True
        else:
            return False

