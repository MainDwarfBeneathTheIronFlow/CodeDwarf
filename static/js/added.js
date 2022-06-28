"use strict";

var durat = 3;

var maxParticles = 20000,
particleSize = 10,
emissionRate = 5,
objectSize = 7;


var canvas = document.querySelector('canvas');
var mainCanvas = document.getElementById('my_canvas');
var ctx = canvas.getContext('2d');


class Particle {
    constructor(point, velocity, acceleration) {
        this.position = point || new Vector(0, 0);
        this.velocity = velocity || new Vector(0, 0);
        this.acceleration = acceleration || new Vector(0, 0);
    }
    move() {
        this.velocity.add(this.acceleration);
        this.position.add(this.velocity);
    }
}

class Field {
    constructor(point, mass) {
        this.position = point;
        this.setMass(mass);
    }
    setMass(mass) {
        this.mass = mass || 100;
        this.drawColor = mass < 0 ? "#f00" : "#0f0";
    }
}

class Vector {
    constructor(x, y) {
        this.x = x || 0;
        this.y = y || 0;
    }
    add(vector) {
        this.x += vector.x;
        this.y += vector.y;
    }
    getMagnitude() {
        return Math.sqrt(this.x * this.x + this.y * this.y);
    }
    getAngle() {
        return Math.atan2(this.y, this.x);
    }
    static fromAngle(angle, magnitude) {
        return new Vector(magnitude * Math.cos(angle), magnitude * Math.sin(angle));
    }
}


class Emitter {
    constructor(point, velocity, spread) {
        this.position = point; // Vector
        this.velocity = velocity; // Vector
        this.spread = spread || Math.PI / 32;
        this.drawColor = "#999";
    }
    emitParticle() {
        var angle = this.velocity.getAngle() + this.spread - Math.random() * this.spread * 2;

        var magnitude = this.velocity.getMagnitude();

        var position = new Vector(this.position.x, this.position.y);

        var velocity = Vector.fromAngle(angle, magnitude);

        return new Particle(position, velocity);
    }
}


function addNewParticles() {
  if (particles.length > maxParticles) return;

  for (var i = 0; i < emitters.length; i++) {

    for (var j = 0; j < emissionRate; j++) {
      particles.push(emitters[i].emitParticle());
    }

  }
}

function plotParticles(boundsX, boundsY) {
  var currentParticles = [];

  for (var i = 0; i < particles.length; i++) {
    var particle = particles[i];
    var pos = particle.position;

    if (pos.x < 0 || pos.x > boundsX || pos.y < 0 || pos.y > boundsY) 
      continue;

    particle.move();
    currentParticles.push(particle);
  }

  particles = currentParticles;
}

function drawParticles() {
  ctx.fillStyle = "#e88000";
  for (var i = 0; i < particles.length; i++) {
    var position = particles[i].position;
    ctx.fillRect(position.x, position.y, particleSize, particleSize);
  }
}

var particles = [];

var midX = canvas.width / 2;
var midY = canvas.height / 2;

var emitters = []

function loop() {
  clear();
  update();
  draw();
  queue();
}

function clear() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function update() {
  addNewParticles();
  plotParticles(canvas.width, canvas.height);
}

function draw() {
  drawParticles();
}

function queue() {
  window.requestAnimationFrame(loop);
}
