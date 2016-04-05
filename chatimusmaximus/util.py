from chatimusmaximus.plugin_wrapper import PluginWrapper


def create_services_from_settings(settings, modules: dict):
    # don't want to pass these arguments in to the plugins
    _rm_arguments = ['connect', 'display_missing']
    # we're going to return these bad boys at the end
    # addresses is a list of zeromq endpoints
    plugin_wrappers = []
    addresses = []

    # need the name of service to check to see if `youtube`
    # service is the platform dict
    for name, service in settings['services'].items():
        # Do this code for everything except youtube
        if not name == 'youtube':
            # the python file that we're going to run is the same
            # as the `name` attribute (I.E. irc, xmpp, etc.)
            module = modules[name]
            # Let's grab the actual values now. `platform` is the
            # name of the platform. (I.E. twitch, livecoding, etc)
            # another way to think of platform is website name
            for platform, platform_settings in service.items():
                # check to see if we want to connect or not.
                # if not, we'll move on to the next service
                if not platform_settings['connect']:
                    continue
                # add the zeromq endpoint addresses to our return list
                addresses.append(platform_settings['socket_address'])
                # PluginWrapper abstracts out the subprocess lib for us
                plugin_wrapper = PluginWrapper(module)
                # create dict with every key having a `--` in front of it
                kwargs = {'--' + key: value
                          for (key, value)
                          in platform_settings.items()
                          if key not in _rm_arguments}

                # add in the service name to kwargs
                kwargs['--service_name'] = platform
                # activate the plugin wrapper and append it to the list
                plugin_wrapper.activate(invoke_kwargs=kwargs)
                plugin_wrappers.append(plugin_wrapper)
        # Do this code for youtube
        else:
            # check to see if we want to connect or not
            if not service['connect']:
                continue
            # add the socket address to the list of zeromq endpoints
            addresses.append(service['socket_address'])
            client_secrets_file = service['api_connect']['client_secrets_file']
            # check to see if using the youtube api
            if client_secrets_file and not client_secrets_file == "":
                print('activating the youtube api!')
                plugin_wrapper = PluginWrapper(modules['youtube_api'])
                kwargs = {'--client_secret_filepath': client_secrets_file,
                          '--socket_address': service['socket_address']}
            # using the javascript webscraper
            else:
                url = service['javascript_scraper']['youtube_url']
                kwargs = {'--url': url,
                          '--comment_element_id': 'all-comments',
                          '--author_class_name': 'yt-user-name',
                          '--message_class_name': 'comment-text',
                          '--socket_address': service['socket_address'],
                          '--service_name': 'youtube'}

                module = modules['javascript_webscraper']
                plugin_wrapper = PluginWrapper(module)
            # activate the youtube module
            plugin_wrapper.activate(invoke_kwargs=kwargs)
            # append it to the list
            plugin_wrappers.append(plugin_wrapper)

    return plugin_wrappers, addresses
