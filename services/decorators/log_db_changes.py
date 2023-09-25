import logging


# class decorator for logging database change operations
def log_database_changes(cls):
    def log_db_operation(method):
        def wrapper(self, request, *args, **kwargs):
            response = method(self, request, *args, **kwargs)
            # create a log entry indicating the method name and the request path
            logging.info(f'Database operation: {method.__name__} {request.path}')
            return response
        return wrapper

    for method_name in ['create', 'update', 'destroy']:
        # get the original method by name from the cls class
        original_method = getattr(cls, method_name)
        # apply the log_db_operation decorator to the original method
        setattr(cls, method_name, log_db_operation(original_method))

    return cls
