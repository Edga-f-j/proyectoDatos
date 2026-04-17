
Guia spring jpa · MD
Copiar

# Guía completa: API REST con Spring Boot + JPA + PostgreSQL
 
> Guía paso a paso para construir una API REST desde cero.  
> Basada en el proyecto **FitZone** — sistema de gestión para un gimnasio.  
> Stack: Spring Boot 3 · Spring Data JPA · PostgreSQL · Docker · Lombok
 
---
 
## Tabla de contenidos
 
1. [Planificación antes de codear](#1-planificación-antes-de-codear)
2. [Crear el proyecto](#2-crear-el-proyecto)
3. [Configurar Docker y la base de datos](#3-configurar-docker-y-la-base-de-datos)
4. [Estructura de paquetes](#4-estructura-de-paquetes)
5. [Capa Persistence — Entities](#5-capa-persistence--entities)
6. [Capa Persistence — Repositories](#6-capa-persistence--repositories)
7. [Capa Service — Interface e Impl](#7-capa-service--interface-e-impl)
8. [Capa Web — Controllers](#8-capa-web--controllers)
9. [DTOs y queries avanzadas](#9-dtos-y-queries-avanzadas)
10. [Validaciones con @Valid](#10-validaciones-con-valid)
11. [Manejo global de excepciones](#11-manejo-global-de-excepciones)
12. [Datos de prueba (data.sql)](#12-datos-de-prueba-datasql)
13. [Pruebas con Postman](#13-pruebas-con-postman)
14. [Errores comunes y cómo resolverlos](#14-errores-comunes-y-cómo-resolverlos)
---
 
## 1. Planificación antes de codear
 
Antes de abrir IntelliJ dedica **10-15 minutos** a planear. Esto evita errores de diseño que después son difíciles de corregir.
 
### 1.1 Diagrama de clases (UML)
 
Dibuja las entidades, sus atributos y las relaciones entre ellas. Herramientas recomendadas:
 
- **draw.io** (diagrams.net) — gratis, en el navegador, tiene plantillas UML
- **dbdiagram.io** — escribes código simple y genera el diagrama automáticamente
**Lo que debe incluir el diagrama:**
- Nombre de cada entidad
- Atributos con su tipo de dato (`String`, `Integer`, `LocalDate`, `BigDecimal`, etc.)
- Los IDs (`idMember`, `idTrainer`, etc.)
- Las relaciones con su multiplicidad (`1` → `0..*`)
**Ejemplo FitZone:**
 
```
Trainer (1) ──────────── (0..*) Plan
                                  │
                                  │ (0..*)
                                  │
Member (1) ──────────── (0..*) Enrollment
```
 
| Entidad | Atributos principales |
|---|---|
| `Trainer` | `idTrainer`, `name`, `specialty`, `hourlyRate: BigDecimal` |
| `Member` | `idMember`, `name`, `email (unique)`, `phone`, `registrationDate: LocalDate` |
| `Plan` | `idPlan`, `name`, `description`, `durationWeeks: Integer`, FK→Trainer |
| `Enrollment` | `idEnrollment`, `startDate`, `endDate`, `status (enum)`, FK→Member, FK→Plan |
 
### 1.2 Tabla de endpoints
 
Antes de codear los controllers, anota qué endpoints vas a implementar. Esto evita paths duplicados y conflictos de URL.
 
| Método | URL | Descripción | Código HTTP |
|---|---|---|---|
| GET | `/api/members` | Listar todos los socios | 200 |
| GET | `/api/members/{id}` | Obtener socio por ID | 200 / 404 |
| POST | `/api/members` | Crear socio | 201 |
| PUT | `/api/members/{id}` | Actualizar socio | 200 |
| DELETE | `/api/members/{id}` | Eliminar socio | 204 |
| GET | `/api/members/name/{name}` | Buscar por nombre | 200 |
| GET | `/api/plans/trainer/{idTrainer}` | Planes de un entrenador | 200 |
| GET | `/api/enrollments/member/{id}/active` | Inscripciones activas de un socio | 200 |
| GET | `/api/enrollments/active/today` | Inscripciones activas hoy | 200 |
| GET | `/api/enrollments/{id}/summary` | Resumen de inscripción (DTO) | 200 / 404 |
| GET | `/api/trainers/{id}/stats` | Estadísticas del entrenador | 200 / 404 |
 
> **Convenciones importantes:**
> - Las URLs siempre en **plural** y con prefijo `/api/`
> - `POST` siempre retorna `201 CREATED`, no `200 OK`
> - `DELETE` siempre retorna `204 No Content`
 
---
 
## 2. Crear el proyecto
 
Ve a [start.spring.io](https://start.spring.io) y configura:
 
| Campo | Valor |
|---|---|
| Project | Gradle - Groovy |
| Language | Java |
| Spring Boot | 3.x.x (la más reciente estable) |
| Group | `com.tuempresa` (o el que prefieras) |
| Artifact | `fitzone` |
| Packaging | Jar |
| Java | 17 o 21 |
 
**Dependencias a seleccionar:**
 
| Dependencia | Para qué sirve |
|---|---|
| Spring Web | Crear los controllers REST |
| Spring Data JPA | Manejar la base de datos con JPA/Hibernate |
| PostgreSQL Driver | Conectar con PostgreSQL |
| Lombok | Reducir código repetitivo (`@Getter`, `@Setter`, etc.) |
| Validation | Validar datos de entrada con `@Valid` |
 
Descarga el proyecto, ábrelo en IntelliJ.
 
### Verificar `build.gradle`
 
Confirma que estas dependencias están presentes:
 
```groovy
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-validation'
    compileOnly 'org.projectlombok:lombok'
    runtimeOnly 'org.postgresql:postgresql'
    annotationProcessor 'org.projectlombok:lombok'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}
```
 
---
 
## 3. Configurar Docker y la base de datos
 
### 3.1 compose.yaml
 
Crea el archivo `compose.yaml` en la raíz del proyecto (al mismo nivel que `build.gradle`):
 
```yaml
services:
  postgres:
    image: 'postgres:latest'
    restart: unless-stopped          # reinicia si el contenedor se cae
    environment:
      - 'POSTGRES_DB=fitZoneDb'      # nombre de la base de datos
      - 'POSTGRES_PASSWORD=fit123'   # contraseña
      - 'POSTGRES_USER=fit'          # usuario
    ports:
      - '5432:5432'                  # puerto local:puerto contenedor
    volumes:
      - pgdata:/data/postgres        # persiste los datos aunque elimines el contenedor
 
volumes:
  pgdata:
```
 
> **Nota:** Cambia `POSTGRES_DB`, `POSTGRES_PASSWORD` y `POSTGRES_USER` por los valores que quieras. Solo asegúrate de que coincidan exactamente con `application.properties`.
 
### 3.2 application.properties
 
En `src/main/resources/application.properties`:
 
```properties
spring.application.name=FitZone
 
# Conexión a PostgreSQL — debe coincidir exactamente con compose.yaml
spring.datasource.driver-class-name=org.postgresql.Driver
spring.datasource.url=jdbc:postgresql://localhost:5432/fitZoneDb
spring.datasource.username=fit
spring.datasource.password=fit123
 
# JPA / Hibernate
spring.jpa.hibernate.ddl-auto=update       # crea/actualiza tablas automáticamente
spring.jpa.show-sql=true                   # muestra las queries SQL en consola
spring.jpa.properties.hibernate.format_sql=true
 
# Inicialización de datos con data.sql
spring.sql.init.mode=always
spring.jpa.defer-datasource-initialization=true
```
 
**¿Qué hace `ddl-auto=update`?**  
Hibernate lee tus entities y crea o actualiza las tablas en la BD automáticamente. Opciones:
- `update` — crea si no existe, actualiza si hay cambios ✅ (para desarrollo)
- `create-drop` — recrea todo al arrancar y borra al cerrar (para tests)
- `none` — no toca la BD (para producción)
### 3.3 Levantar PostgreSQL
 
```bash
# Levantar el contenedor (desde la raíz del proyecto)
docker compose up -d
 
# Verificar que está corriendo
docker ps
 
# Ver logs si algo falla
docker compose logs postgres
```
 
---
 
## 4. Estructura de paquetes
 
Organiza tu código en esta estructura **antes de crear cualquier archivo Java**:
 
```
src/main/java/com/tuempresa/fitzone/
│
├── FitZoneApplication.java
│
├── persistence/
│   ├── entity/
│   │   ├── TrainerEntity.java
│   │   ├── MemberEntity.java
│   │   ├── PlanEntity.java
│   │   └── EnrollmentEntity.java
│   │
│   └── repository/
│       ├── TrainerRepository.java
│       ├── MemberRepository.java
│       ├── PlanRepository.java
│       └── EnrollmentRepository.java
│
├── service/
│   ├── dto/                          ← DTOs van aquí, NO en persistence
│   │   ├── EnrollmentSummaryDto.java
│   │   └── TrainerStatsDto.java
│   │
│   ├── impl/
│   │   ├── TrainerServiceImpl.java
│   │   ├── MemberServiceImpl.java
│   │   ├── PlanServiceImpl.java
│   │   └── EnrollmentServiceImpl.java
│   │
│   ├── TrainerService.java
│   ├── MemberService.java
│   ├── PlanService.java
│   └── EnrollmentService.java
│
└── web/
    ├── config/
    │   └── GlobalExceptionHandler.java
    │
    └── controller/
        ├── TrainerController.java
        ├── MemberController.java
        ├── PlanController.java
        └── EnrollmentController.java
```
 
> **Regla:** Cada capa solo habla con la inmediatamente inferior:
> `Controller → Service → Repository`  
> El controller nunca llama directamente al repository.
 
---
 
## 5. Capa Persistence — Entities
 
Las entities representan las tablas de la base de datos. Empieza siempre por las que **no tienen FK** (llaves foráneas) y termina con las que más dependencias tienen.
 
**Orden correcto para FitZone:** `Trainer` → `Member` → `Plan` → `Enrollment`
 
### 5.1 Entity sin relaciones
 
```java
@Entity
@Table(name = "trainer")
@Getter
@Setter
@NoArgsConstructor
public class TrainerEntity {
 
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_trainer")
    private Integer idTrainer;
 
    @Column(nullable = false, length = 150)
    private String name;
 
    @Column(nullable = false, length = 150)
    private String specialty;
 
    // Para BigDecimal usar precision y scale, NO length
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal hourlyRate;
}
```
 
```java
@Entity
@Table(name = "member")
@Getter
@Setter
@NoArgsConstructor
public class MemberEntity {
 
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_member")
    private Integer idMember;
 
    @Column(nullable = false, length = 100)
    private String name;
 
    @Column(nullable = false, length = 150, unique = true)
    private String email;
 
    // Teléfono siempre String, nunca BigDecimal (perdería el +57 o ceros iniciales)
    @Column(length = 20)
    private String phone;
 
    // LocalDate no necesita length
    @Column(nullable = false)
    private LocalDate registrationDate;
}
```
 
### 5.2 Entity con `@ManyToOne`
 
Cuando una entidad tiene una FK hacia otra, usas `@ManyToOne` + `@JoinColumn`:
 
```java
@Entity
@Table(name = "plan")
@Getter
@Setter
@NoArgsConstructor
public class PlanEntity {
 
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_plan")
    private Integer idPlan;
 
    @Column(nullable = false, length = 150)
    private String name;
 
    private String description;
 
    // Integer no necesita length
    @Column(nullable = false)
    private Integer durationWeeks;
 
    // FK hacia Trainer: un plan pertenece a un entrenador
    @ManyToOne
    @JoinColumn(name = "id_trainer", nullable = false)
    private TrainerEntity trainer;
}
```
 
### 5.3 Entity con Enum
 
Los enums en JPA se guardan en la BD como texto con `@Enumerated(EnumType.STRING)`.  
Define el enum como clase anidada dentro de la entity:
 
```java
@Entity
@Table(name = "enrollment")
@Getter
@Setter
@NoArgsConstructor
public class EnrollmentEntity {
 
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id_enrollment")
    private Integer idEnrollment;
 
    @Column(nullable = false)
    private LocalDate startDate;
 
    @Column(nullable = false)
    private LocalDate endDate;
 
    // Guardado como texto en la BD: "ACTIVE", "COMPLETED", "CANCELED"
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private EnrollmentStatus status;
 
    @ManyToOne
    @JoinColumn(name = "id_member", nullable = false)
    private MemberEntity member;
 
    @ManyToOne
    @JoinColumn(name = "id_plan", nullable = false)
    private PlanEntity plan;
 
    // Enum anidado
    public enum EnrollmentStatus {
        ACTIVE,
        COMPLETED,
        CANCELED
    }
}
```
 
### ⚠️ Errores comunes en entities
 
| Error | Causa | Solución |
|---|---|---|
| `length` en `Integer` o `BigDecimal` | `length` solo aplica a `String` | Quitar `length`. Para `BigDecimal` usar `precision` y `scale` |
| `phone` como `BigDecimal` | Un teléfono no es un número matemático | Usar `String` |
| `@Column(name)` del ID igual al de un `@JoinColumn` | Dos campos apuntan a la misma columna | El nombre del ID debe ser único, ej: `id_enrollment` |
| Falta `@GeneratedValue` | El ID no se autogenera | Siempre acompañar `@Id` con `@GeneratedValue(strategy = GenerationType.IDENTITY)` |
 
---
 
## 6. Capa Persistence — Repositories
 
Los repositories son interfaces que extienden `JpaRepository` y dan acceso a la base de datos. Spring los implementa automáticamente — tú solo declaras los métodos.
 
`JpaRepository<TipoEntidad, TipoDelId>` ya incluye `findAll()`, `findById()`, `save()`, `deleteById()`, etc.
 
### 6.1 Repository básico
 
```java
public interface TrainerRepository extends JpaRepository<TrainerEntity, Integer> {
    // Solo con esto ya tienes CRUD completo
}
```
 
### 6.2 Derived queries (queries por nombre de método)
 
Spring genera el SQL automáticamente leyendo el nombre del método:
 
```java
public interface MemberRepository extends JpaRepository<MemberEntity, Integer> {
 
    // WHERE LOWER(name) LIKE '%name%'
    List<MemberEntity> findByNameContainingIgnoreCase(String name);
}
 
public interface PlanRepository extends JpaRepository<PlanEntity, Integer> {
 
    // El _ navega la relación: plan.trainer.idTrainer
    // Genera: JOIN trainer ON plan.id_trainer = trainer.id_trainer
    //         WHERE trainer.id_trainer = ?
    List<PlanEntity> findByTrainer_IdTrainer(Integer idTrainer);
}
 
public interface EnrollmentRepository extends JpaRepository<EnrollmentEntity, Integer> {
 
    // Combina dos filtros: por socio Y por status
    // WHERE member.id_member = ? AND status = ?
    List<EnrollmentEntity> findByMember_IdMemberAndStatus(
        Integer idMember,
        EnrollmentEntity.EnrollmentStatus status
    );
}
```
 
**Cómo leer un derived query:**
 
```
findBy  Member_IdMember  And  Status
  │          │            │      │
  │          │            │      └── segundo filtro: campo "status"
  │          │            └────────── une filtros con AND
  │          └─────────────────────── navega: enrollment → member → idMember
  └────────────────────────────────── "buscar donde..."
```
 
### 6.3 @Query con JPQL
 
Cuando la lógica es más compleja (fechas del sistema, JOINs de múltiples tablas, agregaciones), escribes la query manualmente con JPQL.
 
> **Diferencia clave:** En JPQL usas nombres de clases y campos Java, NO nombres de tablas y columnas SQL.
 
```java
// Inscripciones activas hoy (startDate <= hoy <= endDate)
@Query("""
    SELECT e FROM EnrollmentEntity e
    WHERE e.status = 'ACTIVE'
    AND e.startDate <= CURRENT_DATE
    AND e.endDate >= CURRENT_DATE
""")
List<EnrollmentEntity> findActiveToday();
```
 
```java
// COUNT para estadísticas
@Query("""
    SELECT COUNT(p)
    FROM PlanEntity p
    WHERE p.trainer.idTrainer = :idTrainer
""")
Long countPlansByTrainer(Integer idTrainer);
 
@Query("""
    SELECT COUNT(e)
    FROM EnrollmentEntity e
    WHERE e.plan.trainer.idTrainer = :idTrainer
    AND e.status = fitzone.persistence.entity.EnrollmentEntity.EnrollmentStatus.ACTIVE
""")
Long countActiveEnrollmentsByTrainer(Integer idTrainer);
```
 
### 6.4 @Query con SELECT new (retorna DTO directamente)
 
```java
@Query("""
    SELECT new fitzone.service.dto.EnrollmentSummaryDto(
        m.name,
        p.name,
        t.name,
        t.specialty,
        e.startDate,
        e.endDate,
        e.status
    )
    FROM EnrollmentEntity e
        JOIN e.member m
        JOIN e.plan p
        JOIN p.trainer t
    WHERE e.idEnrollment = :id
""")
Optional<EnrollmentSummaryDto> findSummaryById(Integer id);
```
 
> **Reglas del `SELECT new`:**
> - El path del DTO debe ser el **paquete completo**: `fitzone.service.dto.EnrollmentSummaryDto`
> - Los parámetros del `SELECT new` deben coincidir **exactamente** en orden y tipo con el constructor del DTO
> - El DTO debe tener ese constructor explícito (no alcanza con `@AllArgsConstructor`)
 
---
 
## 7. Capa Service — Interface e Impl
 
El service contiene la **lógica de negocio**. Siempre se define en dos partes: la interface (contrato) y la implementación.
 
**¿Por qué separar interface e impl?**  
La interface define *qué* hace el service. La impl define *cómo* lo hace. El controller solo conoce la interface — así puedes cambiar la implementación sin tocar el controller.
 
### 7.1 Interface del service
 
```java
public interface MemberService {
 
    List<MemberEntity> findAll();
    MemberEntity findById(Integer id);
    MemberEntity save(MemberEntity member);
    MemberEntity update(Integer id, MemberEntity member);  // id + entity, siempre
    void delete(Integer id);
 
    // Métodos especiales (nombres de negocio, no técnicos)
    List<MemberEntity> findByName(String name);
}
```
 
```java
public interface EnrollmentService {
 
    List<EnrollmentEntity> findAll();
    EnrollmentEntity findById(Integer id);
    EnrollmentEntity save(EnrollmentEntity enrollment);
    EnrollmentEntity update(Integer id, EnrollmentEntity enrollment);
    void delete(Integer id);
 
    List<EnrollmentEntity> findByMemberAndStatus(Integer idMember, EnrollmentEntity.EnrollmentStatus status);
    List<EnrollmentEntity> findActiveToday();
    Optional<EnrollmentSummaryDto> getSummary(Integer id);
}
```
 
### 7.2 Implementación
 
```java
@Service
@RequiredArgsConstructor  // genera constructor con los campos final (inyección por constructor)
public class MemberServiceImpl implements MemberService {
 
    private final MemberRepository memberRepository;
 
    @Override
    public List<MemberEntity> findAll() {
        return memberRepository.findAll();
    }
 
    @Override
    public MemberEntity findById(Integer id) {
        // orElseThrow lanza excepción si no existe — el GlobalExceptionHandler la captura
        return memberRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Miembro con id " + id + " no encontrado"));
    }
 
    @Override
    public MemberEntity save(MemberEntity member) {
        return memberRepository.save(member);
    }
 
    @Override
    public MemberEntity update(Integer id, MemberEntity member) {
        // 1. Buscar el existente (si no existe, lanza error aquí)
        MemberEntity existing = findById(id);
        // 2. Actualizar solo los campos (no reemplazar el objeto completo)
        existing.setName(member.getName());
        existing.setEmail(member.getEmail());
        existing.setPhone(member.getPhone());
        existing.setRegistrationDate(member.getRegistrationDate());
        // 3. Guardar y retornar el actualizado
        return memberRepository.save(existing);
    }
 
    @Override
    public void delete(Integer id) {
        memberRepository.deleteById(id);
    }
 
    @Override
    public List<MemberEntity> findByName(String name) {
        // Nombre del service (findByName) != nombre del repository (findByNameContainingIgnoreCase)
        // El service traduce entre el lenguaje de negocio y el técnico
        return memberRepository.findByNameContainingIgnoreCase(name);
    }
}
```
 
### 7.3 Service que ensambla DTO de múltiples queries
 
Cuando necesitas datos de varias queries, el service los combina:
 
```java
@Override
public Optional<TrainerStatsDto> getStats(Integer id) {
    // 1. Verificar que el trainer existe
    TrainerEntity trainer = trainerRepository.findById(id).orElse(null);
    if (trainer == null) return Optional.empty();
 
    // 2. Ejecutar queries de agregación por separado
    Long totalPlans = trainerRepository.countPlansByTrainer(id);
    Long activeEnrollments = trainerRepository.countActiveEnrollmentsByTrainer(id);
 
    // 3. Construir y retornar el DTO
    return Optional.of(new TrainerStatsDto(
            trainer.getName(),
            totalPlans,
            activeEnrollments
    ));
}
```
 
> **¿Por qué no hacer todo en una sola query?**  
> JPQL tiene limitaciones (por ejemplo, `CASE WHEN` dentro de `COUNT` puede fallar según el proveedor). Es más seguro y más legible dividir en queries simples y combinar en el service.
 
---
 
## 8. Capa Web — Controllers
 
El controller recibe la petición HTTP, llama al service, y retorna la respuesta.
 
### 8.1 CRUD estándar
 
```java
@RestController
@RequestMapping("/api/members")    // prefijo /api/ + plural
@RequiredArgsConstructor
public class MemberController {
 
    private final MemberService memberService;
 
    @GetMapping
    public ResponseEntity<List<MemberEntity>> findAll() {
        return ResponseEntity.ok(memberService.findAll());
    }
 
    @GetMapping("/{id}")
    public ResponseEntity<MemberEntity> findById(@PathVariable Integer id) {
        return ResponseEntity.ok(memberService.findById(id));
    }
 
    // POST retorna 201 CREATED, no 200 OK
    @PostMapping
    public ResponseEntity<MemberEntity> save(@Valid @RequestBody MemberEntity member) {
        return ResponseEntity.status(HttpStatus.CREATED).body(memberService.save(member));
    }
 
    @PutMapping("/{id}")
    public ResponseEntity<MemberEntity> update(@PathVariable Integer id,
                                               @Valid @RequestBody MemberEntity member) {
        return ResponseEntity.ok(memberService.update(id, member));
    }
 
    // DELETE retorna 204 No Content con ResponseEntity<Void>
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Integer id) {
        memberService.delete(id);
        return ResponseEntity.noContent().build();
    }
 
    // Búsqueda especial
    @GetMapping("/name/{name}")
    public ResponseEntity<List<MemberEntity>> findByName(@PathVariable String name) {
        return ResponseEntity.ok(memberService.findByName(name));
    }
}
```
 
### 8.2 Endpoint con status hardcodeado
 
A veces el controller fija un parámetro en vez de recibirlo del cliente:
 
```java
// El cliente no manda el status — la URL ya lo dice: /active
// El service es flexible (acepta cualquier status)
// El controller decide que este endpoint siempre busca ACTIVE
@GetMapping("/member/{idMember}/active")
public ResponseEntity<List<EnrollmentEntity>> findActiveByMember(
        @PathVariable Integer idMember) {
    return ResponseEntity.ok(
        enrollmentService.findByMemberAndStatus(
            idMember,
            EnrollmentEntity.EnrollmentStatus.ACTIVE  // hardcodeado aquí
        )
    );
}
```
 
### 8.3 Endpoint que retorna un Optional (DTO)
 
```java
@GetMapping("/{id}/summary")
public ResponseEntity<EnrollmentSummaryDto> getSummary(@PathVariable Integer id) {
    return enrollmentService.getSummary(id)
            .map(ResponseEntity::ok)                   // si existe → 200 con el DTO
            .orElse(ResponseEntity.notFound().build()); // si no → 404 vacío
}
```
 
### ⚠️ Errores comunes en controllers
 
| Error | Solución |
|---|---|
| `@Autowired` en campo | Usar `@RequiredArgsConstructor` + campo `final` |
| `POST` retorna `200` | Cambiar a `ResponseEntity.status(HttpStatus.CREATED).body(...)` |
| `DELETE` retorna `ResponseEntity<Entity>` | Cambiar a `ResponseEntity<Void>` |
| Dos paths iguales ej: `/search/{name}` y `/search/{species}` | Spring no puede diferenciarlos. Usar `/search/by-name/{name}` y `/search/by-species/{species}`, o usar `@RequestParam` |
| URL sin prefijo ni plural: `/member` | Usar `/api/members` |
 
---
 
## 9. DTOs y queries avanzadas
 
Un **DTO (Data Transfer Object)** es una clase que transporta exactamente los datos que quieres retornar, sin exponer la entity completa.
 
**¿Dónde van los DTOs?** Siempre en `service/dto/` — son contratos de la capa de servicio, no de la persistence.
 
### 9.1 DTO para SELECT new en JPQL
 
Necesita constructor explícito con los parámetros en el mismo orden que el `SELECT new`:
 
```java
package fitzone.service.dto;
 
@Getter
public class EnrollmentSummaryDto {
 
    private final String memberName;
    private final String planName;
    private final String trainerName;
    private final String trainerSpecialty;
    private final LocalDate startDate;
    private final LocalDate endDate;
    private final EnrollmentEntity.EnrollmentStatus status;
 
    // Este constructor debe coincidir EXACTAMENTE con el SELECT new de la query
    public EnrollmentSummaryDto(String memberName, String planName,
                                 String trainerName, String trainerSpecialty,
                                 LocalDate startDate, LocalDate endDate,
                                 EnrollmentEntity.EnrollmentStatus status) {
        this.memberName = memberName;
        this.planName = planName;
        this.trainerName = trainerName;
        this.trainerSpecialty = trainerSpecialty;
        this.startDate = startDate;
        this.endDate = endDate;
        this.status = status;
    }
}
```
 
### 9.2 DTO para estadísticas (ensamblado en service)
 
```java
package fitzone.service.dto;
 
@Getter
public class TrainerStatsDto {
 
    private final String trainerName;
    private final Long totalPlans;
    private final Long activeEnrollments;
 
    public TrainerStatsDto(String trainerName, Long totalPlans, Long activeEnrollments) {
        this.trainerName = trainerName;
        this.totalPlans = totalPlans;
        this.activeEnrollments = activeEnrollments;
    }
}
```
 
### 9.3 Dos formas de construir DTOs
 
| Forma | Cuándo usarla |
|---|---|
| `SELECT new` en JPQL | Cuando todos los datos vienen de un JOIN en una sola query |
| Ensamblar en el service | Cuando necesitas combinar varias queries separadas (ej: COUNT + datos básicos) |
 
---
 
## 10. Validaciones con @Valid
 
Las validaciones evitan que lleguen datos inválidos a la base de datos. Se configuran en dos lugares: las anotaciones en la entity y `@Valid` en el controller.
 
### 10.1 Anotaciones de validación en entities
 
```java
// En MemberEntity
@NotBlank(message = "El nombre es obligatorio")
private String name;
 
@NotBlank(message = "El email es obligatorio")
@Email(message = "El email no tiene formato válido")
private String email;
 
@NotBlank(message = "El teléfono es obligatorio")
private String phone;
 
@NotNull(message = "La fecha de registro es obligatoria")
private LocalDate registrationDate;
 
// En TrainerEntity
@NotBlank(message = "El nombre es obligatorio")
private String name;
 
@NotBlank(message = "La especialidad es obligatoria")
private String specialty;
 
@NotNull(message = "La tarifa es obligatoria")
@DecimalMin(value = "0.0", inclusive = false, message = "La tarifa debe ser mayor a 0")
private BigDecimal hourlyRate;
 
// En PlanEntity
@NotBlank(message = "El nombre del plan es obligatorio")
private String name;
 
@NotNull(message = "La duración es obligatoria")
@Min(value = 1, message = "La duración mínima es 1 semana")
private Integer durationWeeks;
 
// En EnrollmentEntity
@NotNull(message = "La fecha de inicio es obligatoria")
private LocalDate startDate;
 
@NotNull(message = "La fecha de fin es obligatoria")
private LocalDate endDate;
 
@NotNull(message = "El estado es obligatorio")
@Enumerated(EnumType.STRING)
private EnrollmentStatus status;
```
 
**Anotaciones más comunes:**
 
| Anotación | Para qué sirve |
|---|---|
| `@NotNull` | El campo no puede ser `null` |
| `@NotBlank` | El campo no puede ser `null`, vacío ni solo espacios (solo para `String`) |
| `@Email` | Valida formato de email |
| `@Min(value)` | Valor mínimo para números |
| `@Max(value)` | Valor máximo para números |
| `@DecimalMin(value)` | Valor mínimo para `BigDecimal` |
| `@Size(min, max)` | Longitud mínima/máxima de un String |
 
### 10.2 Activar la validación en el controller
 
Agrega `@Valid` antes de `@RequestBody` en los métodos `save` y `update:
 
```java
@PostMapping
public ResponseEntity<MemberEntity> save(@Valid @RequestBody MemberEntity member) {
    return ResponseEntity.status(HttpStatus.CREATED).body(memberService.save(member));
}
 
@PutMapping("/{id}")
public ResponseEntity<MemberEntity> update(@PathVariable Integer id,
                                           @Valid @RequestBody MemberEntity member) {
    return ResponseEntity.ok(memberService.update(id, member));
}
```
 
Si falta `@Valid`, las anotaciones en la entity son ignoradas completamente.
 
---
 
## 11. Manejo global de excepciones
 
Sin un `GlobalExceptionHandler`, cuando algo falla Spring retorna un stack trace enorme. Con él, retornas un JSON limpio con el código HTTP correcto.
 
Crea la clase en `web/config/`:
 
```java
package fitzone.web.config;
 
@RestControllerAdvice
public class GlobalExceptionHandler {
 
    // Captura RuntimeException del service (recurso no encontrado) → 404
    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<Map<String, Object>> handleNotFound(RuntimeException ex) {
        Map<String, Object> error = new HashMap<>();
        error.put("timestamp", LocalDateTime.now());
        error.put("status", 404);
        error.put("error", "Not Found");
        error.put("message", ex.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
 
    // Captura errores de @Valid → 400 con detalle de qué campo falló
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidation(
            MethodArgumentNotValidException ex) {
        Map<String, Object> error = new HashMap<>();
        error.put("timestamp", LocalDateTime.now());
        error.put("status", 400);
        error.put("error", "Bad Request");
 
        // Extrae el mensaje de cada campo que falló
        Map<String, String> fieldErrors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(fe ->
            fieldErrors.put(fe.getField(), fe.getDefaultMessage())
        );
        error.put("fields", fieldErrors);
 
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
    }
}
```
 
**Respuesta cuando falta un recurso (404):**
```json
{
    "timestamp": "2026-04-17T09:27:57.402",
    "status": 404,
    "error": "Not Found",
    "message": "Miembro con id 99 no encontrado"
}
```
 
**Respuesta cuando falla una validación (400):**
```json
{
    "timestamp": "2026-04-17T09:27:57.402",
    "status": 400,
    "error": "Bad Request",
    "fields": {
        "email": "El email no tiene formato válido",
        "name": "El nombre es obligatorio"
    }
}
```
 
---
 
## 12. Datos de prueba (data.sql)
 
Crea el archivo `src/main/resources/data.sql`.
 
> **Orden importante:** inserta primero las tablas sin FK, luego las que dependen de ellas.  
> Orden para FitZone: `trainer` → `member` → `plan` → `enrollment`
 
```sql
-- Trainers (sin FK, van primero)
INSERT INTO trainer (name, specialty, hourly_rate)
VALUES ('Carlos Mendoza', 'Musculación', 45.00),
       ('Laura Ríos', 'Yoga', 35.00),
       ('Andrés Pérez', 'Cardio', 30.00);
 
-- Members (sin FK, van primero)
INSERT INTO member (name, email, phone, registration_date)
VALUES ('Juan García',    'juan@email.com',  '3001234567', '2025-01-10'),
       ('María López',   'maria@email.com', '3109876543', '2025-02-15'),
       ('Pedro Sánchez', 'pedro@email.com', '3207654321', '2025-03-01');
 
-- Plans (FK hacia trainer)
INSERT INTO plan (name, description, duration_weeks, id_trainer)
VALUES ('Plan Básico Musculación', 'Rutina inicial para principiantes', 8,  1),
       ('Plan Yoga Avanzado',      'Posiciones y respiración avanzada',  12, 2),
       ('Plan Cardio Express',     'Rutina de cardio de alta intensidad', 4, 3);
 
-- Enrollments (FK hacia member y plan)
-- Fechas pensadas para probar /active/today (hoy = dentro del rango)
INSERT INTO enrollment (start_date, end_date, status, id_member, id_plan)
VALUES ('2026-03-01', '2026-04-30', 'ACTIVE',    1, 1),  -- activa hoy
       ('2026-01-01', '2026-02-28', 'COMPLETED', 2, 2),  -- ya terminó
       ('2026-04-01', '2026-06-30', 'ACTIVE',    3, 3),  -- activa hoy
       ('2026-04-10', '2026-05-10', 'ACTIVE',    2, 1);  -- activa hoy
```
 
> **Tip:** Si al arrancar la app los datos se duplican cada vez, cambia `spring.sql.init.mode=always` a `spring.sql.init.mode=never` una vez que ya tienes los datos cargados.
 
---
 
## 13. Pruebas con Postman
 
### 13.1 Orden de pruebas recomendado
 
Respetar el orden evita errores de FK (no puedes crear un `Plan` si el `Trainer` no existe):
 
1. **Trainers** — `POST /api/trainers`
2. **Members** — `POST /api/members`
3. **Plans** — `POST /api/plans` (referencia a trainer)
4. **Enrollments** — `POST /api/enrollments` (referencia a member y plan)
5. **Endpoints especiales** — summary, stats, active/today
### 13.2 Ejemplos de body para POST
 
**POST /api/trainers**
```json
{
  "name": "Carlos Mendoza",
  "specialty": "Musculación",
  "hourlyRate": 45.00
}
```
 
**POST /api/members**
```json
{
  "name": "Juan García",
  "email": "juan@email.com",
  "phone": "3001234567",
  "registrationDate": "2025-01-10"
}
```
 
**POST /api/plans**
```json
{
  "name": "Plan Básico",
  "description": "Rutina inicial",
  "durationWeeks": 8,
  "trainer": { "idTrainer": 1 }
}
```
 
**POST /api/enrollments**
```json
{
  "startDate": "2026-04-01",
  "endDate": "2026-06-30",
  "status": "ACTIVE",
  "member": { "idMember": 1 },
  "plan": { "idPlan": 1 }
}
```
 
### 13.3 Checklist de pruebas
 
- [ ] `GET /api/members` → lista de socios
- [ ] `GET /api/members/99` → 404 con JSON de error
- [ ] `POST /api/members` con body vacío `{}` → 400 con campos que fallaron
- [ ] `GET /api/plans/trainer/1` → planes del trainer 1
- [ ] `GET /api/enrollments/member/2/active` → solo las ACTIVE del member 2
- [ ] `GET /api/enrollments/active/today` → inscripciones vigentes hoy
- [ ] `GET /api/enrollments/1/summary` → DTO con datos combinados
- [ ] `GET /api/trainers/1/stats` → nombre + totalPlans + activeEnrollments
---
 
## 14. Errores comunes y cómo resolverlos
 
### Error: `UnknownPathException: Could not resolve attribute 'starDate'`
 
**Causa:** Typo en el nombre del campo dentro de una `@Query` JPQL.  
**Solución:** En JPQL usas nombres de campos Java, no columnas SQL. Verifica que el nombre coincida exactamente con el campo en la entity. Usa `Ctrl + Shift + F` en IntelliJ para buscar el typo en todo el proyecto.
 
```
// ❌ Typo
AND e.starDate <= CURRENT_DATE
 
// ✅ Correcto (igual que el campo en la entity)
AND e.startDate <= CURRENT_DATE
```
 
### Error: `UnsatisfiedDependencyException` al arrancar
 
**Causa:** Hay un error en algún repository o service que impide que Spring cree los beans.  
**Solución:** Lee el `Caused by` al final del stack trace — ahí está el error real. Ignora las primeras líneas del error.
 
### Error: La query JPQL con CASE WHEN falla
 
**Causa:** No todos los proveedores JPA soportan `CASE WHEN` dentro de `COUNT`.  
**Solución:** Divide en dos queries simples y ensambla el resultado en el service.
 
### Error: Los datos del `data.sql` se duplican al reiniciar
 
**Causa:** `spring.sql.init.mode=always` ejecuta el SQL en cada arranque.  
**Solución:** Cambiar a `spring.sql.init.mode=never` una vez que ya tienes los datos, o agregar `INSERT INTO ... ON CONFLICT DO NOTHING` al SQL.
 
### Error: `could not determine data type` o errores raros de tipos
 
**Causa:** Usar `length` en campos que no son `String` (como `Integer`, `BigDecimal`, `LocalDate`).  
**Solución:**
- `String` → usa `length`
- `BigDecimal` → usa `precision` y `scale`
- `Integer`, `LocalDate`, `LocalDateTime` → no necesitan anotaciones de tamaño
### Checklist final antes de arrancar la app
 
- [ ] Docker levantado con `docker compose up -d`
- [ ] Las credenciales en `application.properties` coinciden con `compose.yaml`
- [ ] Todas las entities tienen `@Id` + `@GeneratedValue`
- [ ] Los `@Column(name)` del ID no colisionan con ningún `@JoinColumn(name)`
- [ ] Los nombres en `@Query` coinciden exactamente con los campos Java de la entity
- [ ] En `SELECT new`, el path del DTO incluye el paquete completo
- [ ] El constructor del DTO tiene los mismos parámetros en el mismo orden que el `SELECT new`
- [ ] Los controllers usan `@RequiredArgsConstructor` + campos `final` (no `@Autowired`)
- [ ] Los métodos `save` y `update` en los controllers tienen `@Valid` antes de `@RequestBody`
---
 
*Guía generada durante la construcción del proyecto FitZone — Spring Boot 3 + JPA + PostgreSQL*
