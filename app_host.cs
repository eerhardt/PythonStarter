#:sdk Aspire.AppHost.Sdk@13.0.0-preview.1.25514.9
#:package Aspire.Hosting.Python@13.0.0-preview.1.25514.9

#pragma warning disable ASPIREHOSTINGPYTHON001

var builder = DistributedApplication.CreateBuilder(args);

var apiService = builder.AddPythonApp("apiservice", "./api_service", "app.py")
    .WithUvEnvironment()
    .WithExternalHttpEndpoints();

builder.Build().Run();
