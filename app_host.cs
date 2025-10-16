#:sdk Aspire.AppHost.Sdk@13.0.0-preview.1.25515.7
#:package Aspire.Hosting.Python@13.0.0-preview.1.25515.7
#:package CommunityToolkit.Aspire.Hosting.NodeJS.Extensions@9.8.0
#:package Aspire.Hosting.NodeJs@13.0.0-preview.1.25515.7

#pragma warning disable ASPIREHOSTINGPYTHON001

var builder = DistributedApplication.CreateBuilder(args);

var apiService = builder.AddPythonScript("apiservice", "./api_service", "app.py")
    .WithUvEnvironment()
    .WithHttpEndpoint(env: "PORT")
    .WithExternalHttpEndpoints();

builder.AddViteApp("frontend", "./frontend")
    .WithNpmPackageInstallation()
    .WithReference(apiService)
    .WaitFor(apiService);

builder.Build().Run();
