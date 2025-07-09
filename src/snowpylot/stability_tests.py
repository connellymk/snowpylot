from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class ExtColumnTest:
    """
    ExtColumnTest class for representing results of ExtColumnTest stability test.

    Attributes:
        depth_top: Depth from the surface to the top of the layer with unit
        test_score: Test score
        comment: Comment
        propagation: Whether the test propagated
        num_taps: Number of taps
    """

    # Parsed Properties
    depth_top: Optional[Tuple[float, str]] = None
    test_score: Optional[str] = None
    comment: Optional[str] = None

    # Computed Properties
    propagation: Optional[bool] = None
    num_taps: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the extended column test."""
        return (
            f"\n\t depth_top: {self.depth_top}"
            f"\n\t test_score: {self.test_score}"
            f"\n\t comment: {self.comment}"
            f"\n\t propagation: {self.propagation}"
            f"\n\t num_taps: {self.num_taps}"
        )

    def set_depth_top(self, depth_top: Tuple[float, str]) -> None:
        """
        Set the depth from the surface to the top of the layer.

        Args:
            depth_top: The depth with unit
        """
        self.depth_top = depth_top

    def set_test_score(self, test_score: str) -> None:
        """
        Set the test score and compute derived properties.

        Args:
            test_score: The test score
        """
        self.test_score = test_score

        if test_score and len(test_score) > 4:
            prop_char = test_score[3]
            self.propagation = prop_char == "P"

            num_taps = test_score[4:]
            self.num_taps = num_taps

    def set_comment(self, comment: str) -> None:
        """
        Set the comment.

        Args:
            comment: The comment
        """
        self.comment = comment


@dataclass
class ComprTest:
    """
    ComprTest class for representing results of a Compression Test stability test.

    Attributes:
        depth_top: Depth from the surface to the top of the layer with unit
        fracture_character: Fracture character
        test_score: Test score
        comment: Comment
    """

    depth_top: Optional[Tuple[float, str]] = None
    fracture_character: Optional[str] = None
    test_score: Optional[str] = None
    comment: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the compression test."""
        return (
            f"\n\t depth_top: {self.depth_top}"
            f"\n\t fracture_character: {self.fracture_character}"
            f"\n\t test_score: {self.test_score}"
            f"\n\t comment: {self.comment}"
        )

    def set_depth_top(self, depth_top: Tuple[float, str]) -> None:
        """
        Set the depth from the surface to the top of the layer.

        Args:
            depth_top: The depth with unit
        """
        self.depth_top = depth_top

    def set_fracture_character(self, fracture_character: str) -> None:
        """
        Set the fracture character.

        Args:
            fracture_character: The fracture character
        """
        self.fracture_character = fracture_character

    def set_test_score(self, test_score: str) -> None:
        """
        Set the test score.

        Args:
            test_score: The test score
        """
        self.test_score = test_score

    def set_comment(self, comment: str) -> None:
        """
        Set the comment.

        Args:
            comment: The comment
        """
        self.comment = comment


@dataclass
class RBlockTest:
    """
    RBlockTest class for representing results of a Rutschblock Test.

    Attributes:
        depth_top: Depth from the surface to the top of the layer with unit
        fracture_character: Fracture character
        release_type: Release type
        test_score: Test score
        comment: Comment
    """

    depth_top: Optional[Tuple[float, str]] = None
    fracture_character: Optional[str] = None
    release_type: Optional[str] = None
    test_score: Optional[str] = None
    comment: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the rutschblock test."""
        return (
            f"\n\t depth_top: {self.depth_top}"
            f"\n\t fracture_character: {self.fracture_character}"
            f"\n\t release_type: {self.release_type}"
            f"\n\t test_score: {self.test_score}"
            f"\n\t comment: {self.comment}"
        )

    def set_depth_top(self, depth_top: Tuple[float, str]) -> None:
        """
        Set the depth from the surface to the top of the layer.

        Args:
            depth_top: The depth with unit
        """
        self.depth_top = depth_top

    def set_fracture_character(self, fracture_character: str) -> None:
        """
        Set the fracture character.

        Args:
            fracture_character: The fracture character
        """
        self.fracture_character = fracture_character

    def set_release_type(self, release_type: str) -> None:
        """
        Set the release type.

        Args:
            release_type: The release type
        """
        self.release_type = release_type

    def set_test_score(self, test_score: str) -> None:
        """
        Set the test score.

        Args:
            test_score: The test score
        """
        self.test_score = test_score

    def set_comment(self, comment: str) -> None:
        """
        Set the comment.

        Args:
            comment: The comment
        """
        self.comment = comment


@dataclass
class PropSawTest:
    """
    PropSawTest class for representing results of a Propagation Saw Test.

    Attributes:
        failure: Whether the test failed
        depth_top: Depth from the surface to the top of the layer with unit
        fracture_prop: Fracture propagation
        cut_length: Cut length with unit
        column_length: Column length with unit
        comment: Comment
    """

    failure: Optional[bool] = None
    depth_top: Optional[Tuple[float, str]] = None
    fracture_prop: Optional[str] = None
    cut_length: Optional[Tuple[float, str]] = None
    column_length: Optional[Tuple[float, str]] = None
    comment: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the propagation saw test."""
        return (
            f"\n\t failure: {self.failure}"
            f"\n\t depth_top: {self.depth_top}"
            f"\n\t fracture_prop: {self.fracture_prop}"
            f"\n\t cut_length: {self.cut_length}"
            f"\n\t column_length: {self.column_length}"
            f"\n\t comment: {self.comment}"
        )

    def set_failure(self, failure: bool) -> None:
        """
        Set whether the test failed.

        Args:
            failure: Whether the test failed
        """
        self.failure = failure

    def set_depth_top(self, depth_top: Tuple[float, str]) -> None:
        """
        Set the depth from the surface to the top of the layer.

        Args:
            depth_top: The depth with unit
        """
        self.depth_top = depth_top

    def set_comment(self, comment: str) -> None:
        """
        Set the comment.

        Args:
            comment: The comment
        """
        self.comment = comment

    def set_fracture_prop(self, fracture_prop: str) -> None:
        """
        Set the fracture propagation.

        Args:
            fracture_prop: The fracture propagation
        """
        self.fracture_prop = fracture_prop

    def set_cut_length(self, cut_length: Tuple[float, str]) -> None:
        """
        Set the cut length.

        Args:
            cut_length: The cut length with unit
        """
        self.cut_length = cut_length

    def set_column_length(self, column_length: Tuple[float, str]) -> None:
        """
        Set the column length.

        Args:
            column_length: The column length with unit
        """
        self.column_length = column_length


@dataclass
class StabilityTests:
    """
    StabilityTests class for representing stability tests from a SnowPilot
    caaml.xml file.

    Attributes:
        ECT: List of extended column tests
        CT: List of compression tests
        RBlock: List of rutschblock tests
        PST: List of propagation saw tests
    """

    ECT: List[ExtColumnTest] = field(default_factory=list)
    CT: List[ComprTest] = field(default_factory=list)
    RBlock: List[RBlockTest] = field(default_factory=list)
    PST: List[PropSawTest] = field(default_factory=list)

    def __str__(self) -> str:
        """Return a string representation of the stability tests."""
        stb_tests_str = ""

        for i, ect_test in enumerate(self.ECT):
            stb_tests_str += f"\n    ExtColumnTest {i + 1}: {ect_test}"

        for i, ct_test in enumerate(self.CT):
            stb_tests_str += f"\n    CompressionTest {i + 1}: {ct_test}"

        for i, rblock_test in enumerate(self.RBlock):
            stb_tests_str += f"\n    RutschblockTest {i + 1}: {rblock_test}"

        for i, pst_test in enumerate(self.PST):
            stb_tests_str += f"\n    PropSawTest {i + 1}: {pst_test}"

        return stb_tests_str

    def add_ect(self, ect: ExtColumnTest) -> None:
        """
        Add an extended column test.

        Args:
            ect: The extended column test to add
        """
        self.ECT.append(ect)

    def add_ct(self, ct: ComprTest) -> None:
        """
        Add a compression test.

        Args:
            ct: The compression test to add
        """
        self.CT.append(ct)

    def add_rblock(self, rblock: RBlockTest) -> None:
        """
        Add a rutschblock test.

        Args:
            rblock: The rutschblock test to add
        """
        self.RBlock.append(rblock)

    def add_pst(self, pst: PropSawTest) -> None:
        """
        Add a propagation saw test.

        Args:
            pst: The propagation saw test to add
        """
        self.PST.append(pst)
