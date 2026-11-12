# Custom Service Monitoring Framework

I built a custom Python framework for running service-specific monitoring checks and exposing their results. It worked and provided a useful way to standardize monitoring, but I would no longer build and maintain the execution framework myself. This note preserves the design and the reasoning behind that decision, not an active implementation or a complete copy of the old framework.

> The actual code is not included because that is not important here, the important part is the design and reasoning behind the framework, and the lessons learned from building and maintaining it.

---

## Why monitor service functionality?

Once a service is running, a healthy process or container does not necessarily mean its functionality works for users. Dependencies, configuration, network paths or data synchronization can fail even when the service appears up. Periodically testing important behavior helps detect these problems, including when there is little real user traffic.

Different monitoring approaches complement each other:

- **White-box monitoring (inside-out)** uses signals from inside a system, such as resource usage, application metrics, logs and traces, to show internal health and help diagnose problems.
- **Black-box or synthetic monitoring (outside-in)** actively tests externally observable behavior from a probe's perspective, such as whether DNS resolves or an API returns the expected response. Functional checks can go beyond reachability to exercise a workflow, for example creating, resolving and deleting a test DNS record.

The custom service monitoring framework I initially built focused on these recurring service-specific functional checks, alongside some internal checks such as Kubernetes deployment spread. It was not a replacement for infrastructure monitoring, application telemetry or ordinary pre-deployment tests. Checks only cover the behavior and network paths they exercise, and write operations should use dedicated test resources and safe cleanup.

See [Google's monitoring guide](https://sre.google/sre-book/monitoring-distributed-systems/), [Grafana's synthetic monitoring introduction](https://grafana.com/docs/grafana-cloud/observe-and-act/testing/synthetic-monitoring/introduction/) and [Prometheus alerting practices](https://prometheus.io/docs/practices/alerting/) for more on these concepts and actionable alerts.

---

## The original design

The framework separated reusable monitoring machinery from the checks for an individual service:

```text
Service-specific configuration, context and checks
                 |
                 v
Python monitoring framework
  setup and discovery -> repeated check execution -> results and metrics
                 |                                  |
                 |                                  v
                 |                         Prometheus -> alert rules
                 |                                      |
                 v                                      v
       logs and heartbeat                         Alertmanager
                                                        |
                                                        v
                                                  notifications
```

Services implemented the framework as a Python package and called the `main()` function to run the full monitoring cycle, supplying their own container, configuration, shared context and checks (defined in Python files based on the `Check` and `Test` classes created in the framework). The framework validated and loaded these, refreshed shared resources, ran checks in cycles and handled retries and results. It offered reusable checks for HTTP and transport connectivity, DNS resolution and record lifecycle/synchronization, and Kubernetes deployment spread. Service-specific checks could use the same execution and reporting model.

Results distinguished success, failure, partial results and unexpected errors. The framework logged outcomes and exposed Prometheus metrics for individual tests and execution cycles, including duration and attempts. A heartbeat provided an additional signal that the monitoring process was running. Deployment configuration supplied the monitoring resources and alert rules, while Prometheus and Alertmanager handled alert evaluation, routing and notification state. Alert priorities were not assigned by the Python checks.

This separation was valuable: the service owned its domain checks, the framework reduced duplicated wiring, and the existing alerting infrastructure remained responsible for alerts. The issue was not that the framework was unstable or that building it had no value.

---

## Why move away from it?

The framework was manageable for an early, limited set of services. As more services and checks are added, however, the general-purpose machinery around them tends to grow: scheduling, discovery, configuration, retries, execution isolation, error handling, reporting, extensibility and operational recovery all need design, tests and ongoing support. Every new capability and edge case becomes something I have to maintain alongside the services themselves. However, the more I invest in the framework, the more it becomes a long-term maintenance burden rather than a lightweight aid for service-specific monitoring. Most importantly, managing a growing framework diverts attention from the actual service-specific monitoring that it was meant to simplify. Also, making a monitoring framework is not the core business/where the value is; the value lies in testing the service-specific behavior and ensuring its reliability, not in building and maintaining a custom service monitoring framework.

Much of that machinery already exists in established testing and automation tools. Reimplementing it means owning not only the initial code but also its documentation, compatibility, security updates, bug fixes and future evolution. A custom solution may fit today's requirements closely while still having fewer capabilities, integrations and community resources than a mature alternative. As it grows, its internal abstractions can also make onboarding and changes harder.

The best time to reconsider this is before more services depend on the custom APIs. A stable existing system can continue to serve its current consumers while a replacement is evaluated; stability alone is not a reason to expand a long-term maintenance commitment. Conversely, migration has its own cost and should be justified and verified rather than treated as automatically risk-free. That is exactly what was applied when migrating away from the custom service monitoring framework to existing tools and infrastructure. The transition focused on preserving service-specific checks while offloading the general-purpose machinery to well-supported platforms, minimizing disruption and long-term maintenance overhead.

The lesson is not to avoid custom code entirely. Service-specific probes, domain knowledge and integration glue still need an owner. The distinction is between implementing what is unique to the service and building another general-purpose test runner or alerting system that duplicates existing capabilities without adding significant value (this is core functionality that is needed by many services and is therefore likely already provided by existing tools and infrastructure).

---

## Example solution of reusing existing tools

This is just an example of how existing tools can be combined to replace the custom service monitoring framework. It illustrates the principle of offloading general-purpose machinery to well-supported platforms while keeping service-specific checks under the service owner's control. The important part is not the specific tools chosen, but the separation of concerns and the delegation of general-purpose functionality to well-supported platforms.

> This setup is also the setup used when I migrated away from the custom service monitoring framework at the time, however, it is presented here as an illustrative example rather than a prescriptive solution because different environments and requirements may call for different combinations of tools and approaches. The important point is to focus on the separation of concerns and leveraging well-supported platforms for general-purpose functionality.

One possible setup is to use [Robot Framework](https://robotframework.org/) to define and execute monitoring tests, with small Python libraries or keywords for service-specific checks and integrations. A platform scheduler could run the tests periodically; Robot Framework would provide test execution and result reports. Existing Prometheus and Alertmanager infrastructure could continue to provide metrics, alert evaluation and notifications.

```text
Scheduler -> Robot Framework tests -> results / reports
                         |                  |
                         v                  v
                service-specific     metrics integration -> Prometheus
                Python keywords                              |
                                                            v
                                                     alert rules
                                                            |
                                                            v
                                                     Alertmanager
                                                       /      \
                                              notification  remediation service
                                                               |
                                                               v
                                                    approved recovery action
```

This is an example design, not a claim that the replacement or integrations are already implemented. Robot Framework does not by itself provide the whole monitoring, scheduling or remediation stack. The exact scheduler, metrics integration and recovery mechanism need to be chosen and tested for the environment.

- **Smoke tests, health checks and upgrades:** The same functional scenarios can serve more than continuous monitoring. Select a small, fast subset of critical checks as a [smoke test](https://en.wikipedia.org/wiki/Smoke_testing_(software)) after deployment; run the broader suite as a more detailed health check. A smoke test is deliberately a quick check of simple but critical behavior, not a guarantee that every feature works. The suite can also support upgrade validation: capture a baseline against the current version before an upgrade, then run appropriate checks against the upgraded service. [Helm chart hooks](https://helm.sh/docs/topics/charts_hooks/) like `pre-upgrade` and `post-upgrade` can run Kubernetes Jobs at those lifecycle points and wait for them to complete; a failed hook can fail the Helm release. Configure the deployment process to roll back on failure (for example, `helm upgrade --atomic`) if that is the desired policy—hooks alone do not guarantee rollback. Choose safe, repeatable checks, account for expected changes between versions, and verify any automated rollback.
- **Metrics and freshness:** A small integration could translate test results into bounded per-test metrics, retaining distinctions such as failure, partial results and execution errors where they matter. Decide how to represent these in the new tool rather than assuming a direct mapping. A short-lived scheduled job may exit before Prometheus scrapes it, so use a suitable durable or long-running metrics path. Alert separately on missing or stale results and failed test runs; absence of a result is not success.
- **Alerting:** Keep alert conditions, pending durations and notification routing in the monitoring infrastructure. Alert on actionable service symptoms, and also detect failures of the monitoring pipeline itself. Preserve useful labels without creating unbounded metric cardinality.
- **Automated remediation:** An alert may also be routed to a separate automation service that verifies the condition and runs an approved recovery action, such as restarting a component when appropriate. Keep this optional and independent of notification delivery. Use narrowly scoped permissions, authenticated integrations, idempotent actions, rate limits or cooldowns, audit logs and a way to disable automation. Verify recovery and escalate failures; do not blindly repeat potentially destructive actions.
- **Migration:** Run the new setup alongside the existing one, keeping the old framework stable and limiting changes to necessary fixes only to avoid spending unnecessary effort on the old framework that will be retired in the future anyway. Reuse the service checks and domain concepts where appropriate, compare outcomes and alert behavior, and test missing data, failures, retries and recovery before switching consumers. Roll out incrementally with a rollback path, then retire the old framework only after the replacement is validated.

Robot Framework is an example, not a requirement. Another established test runner, monitoring platform, scheduler or automation tool may fit better. Evaluate maturity, integration, operational requirements, security, licensing, team familiarity and migration cost. No tool needs to provide every desired feature out of the box: a small, well-defined extension can be a better trade-off than owning the entire core. Reusing established tools shifts much of their maintenance to their maintainers and frees time for service-specific improvements, while still leaving responsibility for configuration, upgrades and the integrations I own.

Alternative options include:

- [pytest](https://docs.pytest.org/en/stable/) is a Python test runner suited to checks implemented directly in Python. Scheduling, monitoring integration and alerting remain separate concerns.
- [Grafana k6](https://grafana.com/docs/k6/latest/) supports scripted checks and is particularly focused on performance and load testing. It can also be used for synthetic checks, depending on the deployment.
- [Grafana Synthetic Monitoring](https://grafana.com/docs/grafana-cloud/observe-and-act/testing/synthetic-monitoring/introduction/) provides scheduled black-box checks as part of Grafana Cloud, including scripted checks and alerting integration.
- [Prometheus Blackbox Exporter](https://github.com/prometheus/blackbox_exporter) probes endpoints using protocols such as HTTP, DNS and TCP. It is useful for simpler availability checks, but is not a general-purpose runner for complex service workflows.

These tools have different capabilities and are not interchangeable drop-in replacements; some can also complement one another. Choose based on the checks and operational integration needed.

## References

- [Robot Framework user guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
- [Kubernetes CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [Google SRE: Testing for Reliability](https://sre.google/sre-book/testing-reliability/) (including smoke tests and production tests)
- [Smoke testing](https://en.wikipedia.org/wiki/Smoke_testing_(software))
- [Helm chart hooks](https://helm.sh/docs/topics/charts_hooks/)
- [Prometheus alerting practices](https://prometheus.io/docs/practices/alerting/) and [alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Alertmanager configuration](https://prometheus.io/docs/alerting/latest/configuration/)
- [Prometheus Python client](https://prometheus.github.io/client_python/)