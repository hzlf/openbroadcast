from easy_thumbnails.tests.fields import ThumbnailerFieldTest
from easy_thumbnails.tests.files import FilesTest, EngineTest
from easy_thumbnails.tests.processors import (
    ScaleAndCropTest,
    ColorspaceTest,
    AutocropTest,
    BackgroundTest,
)
from easy_thumbnails.tests.source_generators import PilImageTest
from easy_thumbnails.tests.templatetags import (
    ThumbnailTagTest,
    ThumbnailTagAliasTest,
    ThumbnailerFilterTest,
    ThumbnailerPassiveFilterTest,
)
from easy_thumbnails.tests.models import FileManagerTest
from easy_thumbnails.tests.widgets import ImageClearableFileInput
from easy_thumbnails.tests.aliases import (
    AliasTest,
    AliasThumbnailerTest,
    GenerationTest,
    GlobalGenerationTest,
)
from easy_thumbnails.tests.namers import (
    Default,
    Hashed,
    SourceHashed,
)
