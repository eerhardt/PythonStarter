#pragma warning disable ASPIREHOSTINGPYTHON001

var builder = DistributedApplication.CreateBuilder(args);

var apiService = builder.AddPythonApp("apiservice", "../api_service", "app.py")
    .WithUvEnvironment()
    .WithExternalHttpEndpoints();

builder.Build().Run();
