from jobserver.app import create_app


if __name__ == '__main__':
    import sys
    config_name = sys.argv[1] if len(sys.argv) > 1 else 'default'
    app = create_app(config_name=config_name)
    app.run()
