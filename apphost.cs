#:sdk Aspire.AppHost.Sdk@13.0.0-preview.1.25516.10
#:package Aspire.Hosting.NodeJs@13.0.0-preview.1.25516.10
#:package Aspire.Hosting.Python@13.0.0-preview.1.25516.10
#:package Aspire.Hosting.Redis@13.0.0-preview.1.25516.10
#:package CommunityToolkit.Aspire.Hosting.NodeJS.Extensions@9.8.0

#pragma warning disable ASPIREHOSTINGPYTHON001

var builder = DistributedApplication.CreateBuilder(args);

var cache = builder.AddRedis("cache");

var apiService = builder.AddPythonScript("apiservice", "./api_service", "app.py")
    .WithUvEnvironment()
    .WithReference(cache)
    .WithHttpEndpoint(env: "PORT")
    .WithExternalHttpEndpoints()
    .PublishAsDockerFile(c =>
    {
        c.WithDockerfile(".");
    });

builder.AddViteApp("frontend", "./frontend")
    .WithNpmPackageInstallation()
    .WithReference(apiService)
    .WaitFor(apiService);

builder.Build().Run();
