def get_memento_url(input_url, memento_datetime):
    """
        Given an original URL and a target datetime,
        recursively search for the appropriate Memento URL.
    """

    global original_url
    is_timegate = False

    # START
    # HEAD URI-Q with Accept-Datetime value
    # Go to TEST-0
    response = get_headers(input_url,
		headers={'Accept-Datetime':memento_datetime})

    # FOLLOW
    # URI-Q = Location (value of HTTP header)
    # Go to START
    def follow():
        return get_memento_url(response.headers['Location'], memento_datetime)

	    # TEST-0
	    # IF the response from URI-Q contains "Vary: accept-datetime"
	    #    SET TG-FLAG=TRUE
	    #    SET URI-R=URI-Q
	    # Go to TEST-1
	    if 'accept-datetime' in response.headers['Vary']:
		is_timegate=True
		original_url = input_url

	    # TEST-1
	    # Is URI-Q a Memento?
	    #         YES =>
	    #                 TG-FLAG=FALSE
	    #                 SET URI-R=blank
	    #                 Is the response from URI-Q a 3XX?
	    #                        YES => Go to FOLLOW
	    #                        NO   => STOP SUCCESS
	    #         NO => Go to TEST-2
	    if 'Memento-Datetime' in response.headers:
		is_timegate = False
		original_url = None
		if response.response_code.startswith('3'):
		    return follow()
		else:
		    return input_url

	    # TEST-2 (the poor man's version)
	    # Is the response from URI-Q a 3XX?
	    #         YES => Go to FOLLOW
	    #         NO   => Go to TEST-3
	    if response.response_code.startswith('3'):
		return follow()

	    # TEST-2 (the rich man's version)
	    # Is the response from URI-Q a 3XX?
	    #         YES =>
	    #                 Is TG-FLAG=TRUE?
	    #                         YES => Go to FOLLOW
	    #                         NO   => CASE O1 302 O2. How does the
						user agent handle this?
	    #         NO => Go to TEST-3
	    if response.response_code.startswith('3'):
		if is_timegate:
		    return follow()
		else:
		    raise NotImplementedError()

	    # TEST-3
	    # Is TG-FLAG=TRUE AND Is the response from URI-Q a 4XX or 5XX?
	    #         YES => CASE TimeGate or Memento error. How does the user
				agent handle this?
	    #         NO   => Go to TEST-4
	    if is_timegate and (response.response_code.startswith('4') or
			response.response_code.startswith('5')):
		# TimeGate or Memento error
		raise HttpError()

	    # TEST-4
	    # Does the response from URI-Q have a "timegate" link pointing at URI-G?
	    #    SET TG-FLAG=TRUE
	    #    SET URI-R=URI-Q
	    #    YES => SET URI-Q=URI-G
	    #    NO   => SET URI-Q=URI of the user agent's preferred TimeGate
	    #    Go to START
	    is_timegate = True
	    original_url = input_url
	    new_input_url = response.links.get('timegate', DEFAULT_TIMEGATE+input_url)
	    return get_memento_url(new_input_url, memento_datetime)

