from audiobook_generator import __version__
from audiobook_generator.cli import build_parser


def test_package_version():
    assert __version__ == "1.0.0"


def test_cli_version_action(capsys):
    parser = build_parser()
    try:
        parser.parse_args(["--version"])
    except SystemExit as exc:
        assert exc.code == 0
    else:
        raise AssertionError("--version debe finalizar el parser")

    assert "audiobook-generator 1.0.0" in capsys.readouterr().out
