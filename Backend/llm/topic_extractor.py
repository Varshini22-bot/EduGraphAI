"""
topic_extractor.py

Converts a natural-language question into a topic
that exists in the Neo4j Knowledge Graph.

Example:

"Explain Merge Sort"
        ↓
"Merge Sort"

"Tell me about Binary Search"
        ↓
"Binary Search"

"Quantum Computing"
        ↓
None
"""

import re

from graph.graph_service import GraphService


class TopicExtractor:

    @staticmethod
    def clean_question(question: str) -> str:

        question = question.strip()

        question = re.sub(
            r"\b("
            r"explain|"
            r"describe|"
            r"define|"
            r"what is|"
            r"what are|"
            r"tell me about|"
            r"how does|"
            r"how do|"
            r"give me information about|"
            r"information about"
            r")\b",
            "",
            question,
            flags=re.IGNORECASE
        )

        return question.strip(" ?.!,")


    # ==========================================================
    # MATCHING HELPERS
    # ==========================================================

    # Words that must never decide which topic is retrieved.
    # Without this list, ordinary question words picked the topic:
    # "are" alone appears inside 20 of the 458 node labels
    # ("Local Area Network", ...), so "What are ...?" could be
    # answered about networking regardless of the real subject.
    #
    # Deliberately limited to question scaffolding. Words that do
    # appear inside real labels are NOT listed here - "list"
    # ("Linked List"), "use" ("Use Case"), "point" ("Floating
    # Point"), "word" ("Word Embedding") - because blocking them
    # would stop those topics being found at all.
    STOP_WORDS = {
        "a", "about", "an", "and", "answer", "any", "are", "as",
        "at", "be", "between", "but", "by", "can", "compare",
        "detail", "details", "difference", "differences", "do",
        "does", "for", "from", "give", "has", "have", "how", "i",
        "if", "in", "into", "is", "it", "its", "let", "many",
        "mark", "marks", "me", "more", "much", "my", "not", "of",
        "on", "or", "please", "so", "some", "tell", "than",
        "that", "the", "their", "them", "then", "there", "these",
        "they", "this", "to", "up", "us", "was", "we", "were",
        "what", "when", "where", "which", "who", "why", "will",
        "with", "would", "you", "your",

        # Answer-STYLE instructions. These describe how the student
        # wants the answer written, not what it is about, so they
        # must not count as topic words - without this, "Explain
        # recursion simply" failed to resolve because "simply" was
        # treated as part of the topic.
        #
        # "create" and "depth" are deliberately NOT here: they are
        # real topic words in "Create Operation" and "Depth First
        # Search (DFS)".
        "brief", "briefly", "concise", "easier", "easily", "easy",
        "example", "examples", "note", "notes", "prerequisite",
        "prerequisites", "revision", "show", "simple", "simply",
        "step", "steps", "summary",
    }


    @staticmethod
    def _stem(word: str) -> str:
        """
        Very small plural stripper, applied to BOTH sides of every
        comparison so the two stay consistent. Exists only so
        "sorting algorithms" can still match the label "Algorithm"
        - the old CONTAINS scan matched plurals for free and we
        don't want to lose that recall.
        """

        if len(word) > 5 and word.endswith("es"):

            return word[:-2]

        if (
            len(word) > 4
            and word.endswith("s")
            and not word.endswith("ss")
        ):

            return word[:-1]

        return word


    @staticmethod
    def _normalize(text: str) -> str:
        """
        Lowercase, reduce every run of punctuation/symbols to a
        single space, stem each word, and pad with spaces so that
        `needle in haystack` is a WHOLE-WORD test.

        The padding is the important part: " can " is not a
        substring of " scan scheduling ", which is exactly the
        false match that used to send Merge Sort questions to
        SCAN Scheduling.
        """

        words = re.sub(
            r"[^a-z0-9]+",
            " ",
            text.lower()
        ).split()

        stemmed = [
            TopicExtractor._stem(word)
            for word in words
        ]

        return " " + " ".join(stemmed) + " "


    @staticmethod
    def _significant_sequence(text: str) -> list:
        """
        The stemmed, non-stop-word tokens of a string, IN ORDER - the words
        that are actually allowed to influence topic choice. Order is kept
        so ties can be broken by which topic the question mentions first.
        """

        return [
            word

            for word in TopicExtractor._normalize(text).split()

            if word not in TopicExtractor.STOP_WORDS
            and len(word) > 2
        ]


    @staticmethod
    def _significant_words(text: str) -> set:
        """
        Set form of _significant_sequence, for overlap tests.
        """

        return set(
            TopicExtractor._significant_sequence(text)
        )



    @staticmethod
    def _acronyms(label: str) -> set:
        """
        The bracketed short forms a label carries, e.g.
        "Breadth First Search (BFS)" -> {"bfs"}. These are matched
        exactly (never as substrings), so they can't repeat the old
        bug where a fragment of one word matched another word.
        """

        acronyms = set()

        for group in re.findall(r"\(([^)]*)\)", label):

            for word in TopicExtractor._normalize(group).split():

                if len(word) > 1:

                    acronyms.add(word)

        return acronyms


    PRONOUN_PATTERN = re.compile(r"\b(it|this|that|its|itself)\b", re.IGNORECASE)

    FOLLOW_UP_INTENT_PHRASES = [
        "how does it work",
        "how it works",
        "working principle",
        "working of",
        "time complexity",
        "space complexity",
        "complexity",
        "give an example",
        "give example",
        "show an example",
        "worked example",
        "advantages",
        "disadvantages",
        "limitations",
        "benefits",
        "drawbacks",
        "applications",
        "uses of",
        "more simply",
        "in detail",
        "more detail",
        "detailed explanation",
        "revision notes",
        "viva questions",
        "exam questions",
        "short quiz",
        "prerequisites",
        "related concepts",
        "compare",
    ]


    @staticmethod
    def extract_topic(question: str, context_topic: str = None):

        if not question or not question.strip():

            return None


        # --------------------------------------------------
        # Step 1: Clean the question
        # --------------------------------------------------

        cleaned_question = TopicExtractor.clean_question(
            question
        )


        if not cleaned_question:

            return None


        # --------------------------------------------------
        # Step 2: Load every topic label in ONE round trip
        #
        # Previously this method fired a separate Neo4j
        # CONTAINS scan for the whole question and then one
        # more for EVERY word of length >= 3, returning the
        # first hit. Matching locally instead means one query
        # regardless of how long the question is, and lets us
        # pick the BEST match rather than the first one.
        # --------------------------------------------------

        labels = GraphService.get_all_topic_labels()


        if not labels:

            return None


        has_valid_context = bool(context_topic and context_topic in labels)
        has_pronoun = bool(TopicExtractor.PRONOUN_PATTERN.search(question))
        q_lower = question.lower()
        has_followup_phrase = any(
            phrase in q_lower for phrase in TopicExtractor.FOLLOW_UP_INTENT_PHRASES
        )

        haystack = TopicExtractor._normalize(
            cleaned_question
        )


        # --------------------------------------------------
        # Step 3: Longest label that appears in the question
        #         as a whole phrase
        #
        # Whole-word matching is what fixes the wrong-topic
        # bug. The old per-word CONTAINS scan matched INSIDE
        # words, so "can" in "Can you tell me about Merge
        # Sort" matched "S-CAN Scheduling", "the" matched
        # "THEta-notation", and "for" matched "PerFORmance" -
        # the answer was then grounded on the wrong node.
        #
        # Longest-match-wins is what keeps "Binary Search"
        # from being beaten by a bare "Search", and lets
        # "Binary Search Tree" win over "Binary Search" when
        # the question really is about the tree.
        # --------------------------------------------------

        best_label = None
        best_length = 0

        for label in labels:

            needle = TopicExtractor._normalize(label)

            if needle == " ":

                continue

            if needle in haystack and len(needle) > best_length:

                best_label = label
                best_length = len(needle)


        if best_label:

            # If user asked about a generic single-word label like "Algorithm" or "Process"
            # while using pronouns or follow-up phrasing with an active context_topic,
            # anchor on context_topic instead of drifting.
            if has_valid_context and (has_pronoun or has_followup_phrase):
                if len(best_label.split()) == 1 and best_label.lower() != context_topic.lower():
                    return context_topic

            return best_label


        # Step 3b: If context_topic is active and question has pronouns or follow-up phrasing
        if has_valid_context and (has_pronoun or has_followup_phrase):
            return context_topic


        # --------------------------------------------------
        # Step 4: Fall back to significant-word overlap
        #
        # Handles phrasings that never contain a label
        # verbatim, e.g. "Compare BFS and DFS" against the
        # label "Breadth First Search (BFS)". Stop words are
        # excluded so they can no longer decide the topic,
        # and the label matching the largest FRACTION of
        # itself wins, so a precise short label beats a long
        # one that only overlaps by a single common word.
        # --------------------------------------------------

        question_sequence = TopicExtractor._significant_sequence(
            cleaned_question
        )

        question_words = set(question_sequence)


        if not question_words:

            # If all words were stripped as stop words (e.g. "explain it more simply")
            # and we have an active context topic, stay on context_topic
            if has_valid_context:
                return context_topic

            return None


        # --------------------------------------------------
        # Step 4: Acronym match
        #
        # Covers the case where the student uses the short
        # form the label only carries in brackets, e.g.
        # "Compare BFS and DFS" against the label
        # "Breadth First Search (BFS)". The topic mentioned
        # FIRST wins, so this question anchors on BFS rather
        # than on whichever of the two happens to have been
        # imported into Neo4j first.
        # --------------------------------------------------

        acronym_label = None
        acronym_position = None

        for label in labels:

            for acronym in TopicExtractor._acronyms(label):

                if acronym not in question_words:

                    continue

                position = question_sequence.index(acronym)

                if (
                    acronym_position is None
                    or position < acronym_position
                ):

                    acronym_label = label
                    acronym_position = position


        if acronym_label:

            return acronym_label


        # --------------------------------------------------
        # Step 5: Whole-question coverage
        #
        # Last resort, for phrasings that don't contain a
        # label verbatim: accept a label ONLY if it accounts
        # for EVERY significant word in the question. So
        # "Floating Point" resolves to "Floating Point
        # Number" (both question words are explained by that
        # label), but "Quantum Computing" does NOT resolve to
        # "Cloud Computing", because "quantum" would be left
        # unexplained.
        #
        # That strictness is deliberate. A topic genuinely
        # missing from the Knowledge Graph must come back as
        # None so RAGService can say so - answering confidently
        # about a near-miss node is the exact failure this
        # rewrite exists to remove.
        # --------------------------------------------------

        best_label = None
        best_score = None

        for label in labels:

            label_words = TopicExtractor._significant_words(
                label
            )

            if not label_words:

                continue

            if not question_words.issubset(label_words):

                continue

            score = (
                len(question_words) / len(label_words),
                -len(label_words),
            )

            if best_score is None or score > best_score:

                best_label = label
                best_score = score


        if best_label:

            return best_label


        # Final context fallback if user had active topic and asked something without a new topic
        if has_valid_context and (has_pronoun or has_followup_phrase):

            return context_topic


        # --------------------------------------------------
        # Step 6: Unknown topic
        #
        # Returning None is correct here - RAGService treats
        # it as "not in the Knowledge Graph" and says so,
        # which is far better than the old behaviour of
        # confidently answering about an unrelated node.
        # --------------------------------------------------

        return None
