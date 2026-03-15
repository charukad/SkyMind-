from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List, Any

class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models."""
    pass

class Airport(Base):
    __tablename__ = "airports"

    iata_code: Mapped[str] = mapped_column(String(3), primary_key=True, index=True)
    icao_code: Mapped[Optional[str]] = mapped_column(String(4), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(50))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    congestion_index: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    departing_flights: Mapped[List["Flight"]] = relationship(
        "Flight", foreign_keys="[Flight.origin_iata]", back_populates="origin_airport"
    )
    arriving_flights: Mapped[List["Flight"]] = relationship(
        "Flight", foreign_keys="[Flight.destination_iata]", back_populates="destination_airport"
    )

class Airline(Base):
    __tablename__ = "airlines"

    iata_code: Mapped[str] = mapped_column(String(2), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    country: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    flights: Mapped[List["Flight"]] = relationship("Flight", back_populates="airline")

class Aircraft(Base):
    __tablename__ = "aircraft"

    tail_number: Mapped[str] = mapped_column(String(20), primary_key=True, index=True)
    airline_iata: Mapped[str] = mapped_column(String(2), ForeignKey("airlines.iata_code"))
    model: Mapped[str] = mapped_column(String(100))
    manufacturer: Mapped[str] = mapped_column(String(100))
    capacity: Mapped[int] = mapped_column(Integer)
    maintenance_status: Mapped[str] = mapped_column(String(20), default="NORMAL") # NORMAL, WARNING, CRITICAL
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    flights: Mapped[List["Flight"]] = relationship("Flight", back_populates="aircraft")

class Flight(Base):
    __tablename__ = "flights"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True) # e.g. "EK202-20260315"
    flight_number: Mapped[str] = mapped_column(String(10), index=True) # e.g. "EK202"
    airline_iata: Mapped[str] = mapped_column(String(2), ForeignKey("airlines.iata_code"))
    aircraft_tail: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("aircraft.tail_number"))
    
    origin_iata: Mapped[str] = mapped_column(String(3), ForeignKey("airports.iata_code"))
    destination_iata: Mapped[str] = mapped_column(String(3), ForeignKey("airports.iata_code"))

    # Scheduled Times
    scheduled_departure: Mapped[datetime] = mapped_column(DateTime, index=True)
    scheduled_arrival: Mapped[datetime] = mapped_column(DateTime, index=True)
    
    # Actual/Estimated Times
    actual_departure: Mapped[Optional[datetime]] = mapped_column(DateTime)
    actual_arrival: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Status & ML Outputs
    status: Mapped[str] = mapped_column(String(20), default="SCHEDULED") # SCHEDULED, ACTIVE, DELAYED, CANCELLED, ARRIVED
    delay_probability: Mapped[Optional[float]] = mapped_column(Float)
    expected_delay_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    risk_score: Mapped[Optional[float]] = mapped_column(Float)
    ml_explanation: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    airline: Mapped["Airline"] = relationship("Airline", back_populates="flights")
    aircraft: Mapped[Optional["Aircraft"]] = relationship("Aircraft", back_populates="flights")
    origin_airport: Mapped["Airport"] = relationship("Airport", foreign_keys=[origin_iata], back_populates="departing_flights")
    destination_airport: Mapped["Airport"] = relationship("Airport", foreign_keys=[destination_iata], back_populates="arriving_flights")
    weather_events: Mapped[List["WeatherEvent"]] = relationship("WeatherEvent", back_populates="flight")

class WeatherEvent(Base):
    __tablename__ = "weather_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    airport_iata: Mapped[str] = mapped_column(String(3), ForeignKey("airports.iata_code"), index=True)
    flight_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("flights.id"))
    
    condition: Mapped[str] = mapped_column(String(50)) # e.g. THUNDERSTORM, SNOW, CLEAR
    severity_score: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    
    # Relationships
    airport: Mapped["Airport"] = relationship("Airport")
    flight: Mapped[Optional["Flight"]] = relationship("Flight", back_populates="weather_events")
