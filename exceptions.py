class IncorrectAPIKey(Exception):
    pass


class LLMInitializationError(Exception):
    pass


class PathError(Exception):
    pass


class NotFoundDocuments(Exception):
    pass


class FileLoaderError(Exception):
    pass


class TableinfoDataframeError(Exception):
    pass


class VectordbCreationError(Exception):
    pass


class VectordbLoaderError(Exception):
    pass


class EmbeddingsInitializationError(Exception):
    pass


class TextSplitError(Exception):
    pass


class ErrorGeneratingAnswer(Exception):
    pass


class ErrorGeneratingSummary(Exception):
    pass


class CSVLogUpdateError(Exception):
    pass


class OpenAIError(Exception):
    pass


class MetadataGenerationError(Exception):
    pass


class SchemaDetailsError(Exception):
    pass


class ModelLoadingError(Exception):
    pass

class TokenizerLoadingError(Exception):
    pass

class ElasticSearchConnectionError(Exception):
    pass

class ErrorCheckingIndex(Exception):
    pass

class ErrorDeletingIndex(Exception):
    pass

class ErrorCreatingIndex(Exception):
    pass

class ErrorIndexingData(Exception):
    pass

class ErrorSearchingData(Exception):
    pass

class ErrorScrapingData(Exception):
    pass

class WindowsIntegratedConnectionError(Exception):
    pass

class ModelProcessorLoadingError(Exception):
    pass

class VectordbMergingError(Exception):
    pass